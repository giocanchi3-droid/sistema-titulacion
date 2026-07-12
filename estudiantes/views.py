from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegistroTitulacionForm
from .models import RegistroTitulacion


SECCIONES = [
    (
        "1. Información personal e institucional",
        [
            "id_banner",
            "nombres_completos",
            "cedula",
            "celular",
            "correo_personal",
            "correo_instituc",
            "sede",
            "programa",
            "programa_desc",
        ],
    ),
    (
        "2. Información académica y titulación",
        [
            "numero_cohorte",
            "periodo_ingreso",
            "nivel2",
            "modalidad_titulacion",
            "matricula_uic",
            "periodo_titulacion_senescyt",
            "estado",
            "cumplimiento_idioma",
        ],
    ),
    (
        "3. Prácticas preprofesionales y servicio comunitario",
        [
            "materia_practicas_pre_profesionales",
            "horas_240",
            "materia_servicio_comunitario",
            "horas_120",
        ],
    ),
    (
        "4. Tutor y tema del proyecto",
        [
            "nombres_completos_tutor",
            "id_tutor",
            "tema",
        ],
    ),
    (
        "5. Miembros del tribunal",
        [
            "primer_miembro_tribunal",
            "primer_miembro_id_docente",
            "segundo_miembro_tribunal",
            "segundo_miembro_id_docente",
            "tercer_miembro_tribunal",
            "tercer_miembro_id_docente",
            "cuarto_miembro_tribunal",
            "cuarto_miembro_id_docente",
        ],
    ),
    (
        "6. Calificaciones",
        [
            "proyecto_escrito",
            "defensa_oral",
            "nota_final",
            "examen_teorico_complexivo",
            "examen_teorico_practico",
            "nota_final2",
        ],
    ),
    (
        "7. Observaciones, envío y fecha de grado",
        [
            "observacion_puce_tec",
            "observaciones_secretaria_general",
            "nueva_observacion_puce_tec",
            "estado_envio_registro",
            "fecha_grado",
            "observacion_secretaria",
        ],
    ),
]


def construir_secciones_formulario(form):
    secciones = []

    for titulo, nombres_campos in SECCIONES:
        campos = [
            form[nombre]
            for nombre in nombres_campos
        ]

        secciones.append(
            (titulo, campos)
        )

    return secciones


def construir_secciones_detalle(registro):
    secciones = []

    for titulo, nombres_campos in SECCIONES:
        campos = []

        for nombre in nombres_campos:
            campo_modelo = registro._meta.get_field(nombre)
            metodo_display = getattr(
                registro,
                f"get_{nombre}_display",
                None,
            )

            if metodo_display:
                valor = metodo_display()
            else:
                valor = getattr(registro, nombre)

            if valor is None or valor == "":
                valor = "—"

            campos.append(
                (
                    campo_modelo.verbose_name,
                    valor,
                )
            )

        secciones.append(
            (titulo, campos)
        )

    return secciones


@login_required
def lista_registros(request):
    consulta = request.GET.get("q", "").strip()

    registros = RegistroTitulacion.objects.all()

    if consulta:
        registros = registros.filter(
            Q(cedula__icontains=consulta)
            | Q(nombres_completos__icontains=consulta)
            | Q(id_banner__icontains=consulta)
            | Q(programa__icontains=consulta)
            | Q(nombres_completos_tutor__icontains=consulta)
        )

    contexto = {
        "registros": registros,
        "consulta": consulta,
    }

    return render(
        request,
        "estudiantes/lista.html",
        contexto,
    )


@login_required
def crear_registro(request):
    if request.method == "POST":
        form = RegistroTitulacionForm(request.POST)

        if form.is_valid():
            registro = form.save()

            messages.success(
                request,
                "La información fue almacenada correctamente.",
            )

            return redirect(
                "estudiantes:detalle",
                pk=registro.pk,
            )
    else:
        form = RegistroTitulacionForm()

    contexto = {
        "form": form,
        "titulo": "Registrar información de titulación",
        "texto_boton": "Guardar toda la información",
        "secciones": construir_secciones_formulario(form),
    }

    return render(
        request,
        "estudiantes/formulario.html",
        contexto,
    )


@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(
        RegistroTitulacion,
        pk=pk,
    )

    if request.method == "POST":
        form = RegistroTitulacionForm(
            request.POST,
            instance=registro,
        )

        if form.is_valid():
            registro = form.save()

            messages.success(
                request,
                "La información fue actualizada correctamente.",
            )

            return redirect(
                "estudiantes:detalle",
                pk=registro.pk,
            )
    else:
        form = RegistroTitulacionForm(
            instance=registro,
        )

    contexto = {
        "form": form,
        "registro": registro,
        "titulo": "Editar información de titulación",
        "texto_boton": "Guardar cambios",
        "secciones": construir_secciones_formulario(form),
    }

    return render(
        request,
        "estudiantes/formulario.html",
        contexto,
    )


@login_required
def detalle_registro(request, pk):
    registro = get_object_or_404(
        RegistroTitulacion,
        pk=pk,
    )

    contexto = {
        "registro": registro,
        "secciones_detalle": construir_secciones_detalle(
            registro
        ),
    }

    return render(
        request,
        "estudiantes/detalle.html",
        contexto,
    )


@login_required
def eliminar_registro(request, pk):
    registro = get_object_or_404(
        RegistroTitulacion,
        pk=pk,
    )

    if request.method == "POST":
        registro.delete()

        messages.success(
            request,
            "El registro fue eliminado correctamente.",
        )

        return redirect(
            "estudiantes:lista"
        )

    return render(
        request,
        "estudiantes/confirmar_eliminar.html",
        {
            "registro": registro,
        },
    )
