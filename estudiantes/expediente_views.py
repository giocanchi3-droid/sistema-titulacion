from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldError
from django.shortcuts import get_object_or_404, render

from .models import RegistroTitulacion
from .services_expediente import construir_requisitos


def obtener_actas(registro):
    """
    Obtiene las actas asociadas sin provocar un error
    si el módulo documental todavía no está disponible.
    """

    try:
        modelo_acta = apps.get_model(
            "documentos",
            "Acta",
        )
    except LookupError:
        return []

    try:
        return modelo_acta.objects.filter(
            registro_id=registro.pk
        ).order_by(
            "-fecha_creacion"
        )
    except FieldError:
        return []


def obtener_archivos(registro):
    """
    Deja preparado el expediente para el futuro
    centro documental.
    """

    try:
        modelo_archivo = apps.get_model(
            "documentos",
            "ArchivoExpediente",
        )
    except LookupError:
        return []

    posibles_campos = [
        "registro_id",
        "estudiante_id",
    ]

    for campo in posibles_campos:
        try:
            return modelo_archivo.objects.filter(
                **{
                    campo: registro.pk,
                }
            ).order_by(
                "-fecha_carga"
            )
        except FieldError:
            continue

    return []


def obtener_historial(registro):
    """
    Deja preparada la sección para la línea de tiempo.
    """

    posibles_modelos = [
        (
            "procesos",
            "HistorialEstado",
        ),
        (
            "estudiantes",
            "HistorialExpediente",
        ),
    ]

    for app_label, modelo in posibles_modelos:
        try:
            modelo_historial = apps.get_model(
                app_label,
                modelo,
            )
        except LookupError:
            continue

        posibles_campos = [
            "registro_id",
            "estudiante_id",
            "proceso__estudiante_id",
        ]

        for campo in posibles_campos:
            try:
                return modelo_historial.objects.filter(
                    **{
                        campo: registro.pk,
                    }
                ).order_by(
                    "-fecha"
                )[:20]
            except FieldError:
                continue

    return []


@login_required
def expediente_registro(request, pk):
    registro = get_object_or_404(
        RegistroTitulacion,
        pk=pk,
    )

    avance = construir_requisitos(
        registro
    )

    actas = obtener_actas(
        registro
    )

    archivos = obtener_archivos(
        registro
    )

    historial = obtener_historial(
        registro
    )

    contexto = {
        "registro": registro,
        "avance": avance,
        "actas": actas,
        "archivos": archivos,
        "historial": historial,
    }

    return render(
        request,
        "estudiantes/expediente.html",
        contexto,
    )
