from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from estudiantes.models import RegistroTitulacion

from .forms import ActaForm
from .models import Acta
from .services import generar_archivos_acta


@login_required
def lista_actas(request):
    consulta = request.GET.get(
        "q",
        "",
    ).strip()

    estado = request.GET.get(
        "estado",
        "",
    ).strip()

    actas = (
        Acta.objects
        .select_related(
            "registro",
            "creado_por",
        )
        .all()
    )

    if consulta:
        actas = actas.filter(
            Q(numero_acta__icontains=consulta)
            | Q(
                registro__cedula__icontains=consulta
            )
            | Q(
                registro__nombres_completos__icontains=consulta
            )
            | Q(
                registro__programa__icontains=consulta
            )
        )

    if estado:
        actas = actas.filter(
            estado=estado
        )

    contexto = {
        "actas": actas,
        "consulta": consulta,
        "estado_seleccionado": estado,
        "estados": Acta.ESTADOS,
    }

    return render(
        request,
        "documentos/lista_actas.html",
        contexto,
    )


@login_required
def crear_acta(request):
    registro_id = request.GET.get(
        "registro"
    )

    valores_iniciales = {}

    if registro_id:
        registro = get_object_or_404(
            RegistroTitulacion,
            pk=registro_id,
        )

        valores_iniciales["registro"] = registro

        if registro.modalidad_titulacion:
            valores_iniciales["tipo_acta"] = (
                registro.modalidad_titulacion
            )

    if request.method == "POST":
        form = ActaForm(
            request.POST
        )

        if form.is_valid():
            acta = form.save(
                commit=False
            )

            acta.creado_por = request.user
            acta.save()

            messages.success(
                request,
                "El acta fue registrada como borrador.",
            )

            return redirect(
                "documentos:detalle_acta",
                pk=acta.pk,
            )
    else:
        form = ActaForm(
            initial=valores_iniciales
        )

    return render(
        request,
        "documentos/formulario_acta.html",
        {
            "form": form,
            "titulo": "Crear acta",
            "texto_boton": "Guardar acta",
        },
    )


@login_required
def detalle_acta(request, pk):
    acta = get_object_or_404(
        Acta.objects.select_related(
            "registro",
            "creado_por",
        ),
        pk=pk,
    )

    return render(
        request,
        "documentos/detalle_acta.html",
        {
            "acta": acta,
            "registro": acta.registro,
        },
    )


@login_required
def editar_acta(request, pk):
    acta = get_object_or_404(
        Acta,
        pk=pk,
    )

    if request.method == "POST":
        form = ActaForm(
            request.POST,
            instance=acta,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "El acta fue actualizada correctamente.",
            )

            return redirect(
                "documentos:detalle_acta",
                pk=acta.pk,
            )
    else:
        form = ActaForm(
            instance=acta,
        )

    return render(
        request,
        "documentos/formulario_acta.html",
        {
            "form": form,
            "acta": acta,
            "titulo": "Editar acta",
            "texto_boton": "Guardar cambios",
        },
    )


@login_required
def generar_acta(request, pk):
    acta = get_object_or_404(
        Acta,
        pk=pk,
    )

    if request.method == "POST":
        generar_archivos_acta(
            acta
        )

        messages.success(
            request,
            "El acta fue generada en Word y PDF.",
        )

    return redirect(
        "documentos:detalle_acta",
        pk=acta.pk,
    )


@login_required
def aprobar_acta(request, pk):
    acta = get_object_or_404(
        Acta,
        pk=pk,
    )

    if request.method == "POST":
        if not acta.archivo_pdf or not acta.archivo_word:
            messages.error(
                request,
                "Primero debes generar los archivos Word y PDF.",
            )
        else:
            acta.estado = "APROBADA"
            acta.save(
                update_fields=[
                    "estado",
                    "fecha_actualizacion",
                ]
            )

            messages.success(
                request,
                "El acta fue aprobada.",
            )

    return redirect(
        "documentos:detalle_acta",
        pk=acta.pk,
    )


@login_required
def anular_acta(request, pk):
    acta = get_object_or_404(
        Acta,
        pk=pk,
    )

    if request.method == "POST":
        acta.estado = "ANULADA"
        acta.save(
            update_fields=[
                "estado",
                "fecha_actualizacion",
            ]
        )

        messages.success(
            request,
            "El acta fue anulada.",
        )

    return redirect(
        "documentos:detalle_acta",
        pk=acta.pk,
    )


@login_required
def eliminar_acta(request, pk):
    acta = get_object_or_404(
        Acta,
        pk=pk,
    )

    if request.method == "POST":
        if acta.archivo_word:
            acta.archivo_word.delete(
                save=False
            )

        if acta.archivo_pdf:
            acta.archivo_pdf.delete(
                save=False
            )

        acta.delete()

        messages.success(
            request,
            "El acta fue eliminada.",
        )

        return redirect(
            "documentos:lista_actas"
        )

    return render(
        request,
        "documentos/confirmar_eliminar_acta.html",
        {
            "acta": acta,
        },
    )
