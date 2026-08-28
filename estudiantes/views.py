from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProgramaForm, RegistroTitulacionForm
from .models import HistorialExpediente, Programa, RegistroTitulacion
from .services_excel import exportar_registro_excel


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


def registrar_cambios(registro, anterior, usuario, accion="EDICION"):
    responsable = getattr(usuario, "username", None) or "Sistema"

    for campo in RegistroTitulacionForm.Meta.fields:
        viejo = str(getattr(anterior, campo, "") or "")
        nuevo = str(getattr(registro, campo, "") or "")

        if viejo != nuevo:
            HistorialExpediente.objects.create(
                registro=registro,
                responsable=responsable,
                campo=registro._meta.get_field(campo).verbose_name,
                valor_anterior=viejo,
                valor_nuevo=nuevo,
                accion=accion,
            )


def opciones_programas():
    return Programa.objects.filter(activo=True)


def guardar_programa_catalogo(registro):
    if registro.programa and registro.programa_desc:
        Programa.objects.get_or_create(
            codigo=registro.programa,
            defaults={"descripcion": registro.programa_desc},
        )


@login_required
def lista_registros(request):
    consulta = request.GET.get("q", "").strip()
    programa_seleccionado = request.GET.get(
        "programa",
        "",
    ).strip()
    modalidad_seleccionada = request.GET.get(
        "modalidad",
        "",
    ).strip()
    estado_seleccionado = request.GET.get(
        "estado",
        "",
    ).strip()

    registros_base = RegistroTitulacion.objects.all()
    registros = registros_base

    if consulta:
        registros = registros.filter(
            Q(cedula__icontains=consulta)
            | Q(nombres_completos__icontains=consulta)
            | Q(id_banner__icontains=consulta)
            | Q(programa__icontains=consulta)
            | Q(nombres_completos_tutor__icontains=consulta)
        )

    if programa_seleccionado:
        registros = registros.filter(
            programa=programa_seleccionado
        )

    if modalidad_seleccionada:
        registros = registros.filter(
            modalidad_titulacion=modalidad_seleccionada
        )

    if estado_seleccionado:
        registros = registros.filter(
            estado=estado_seleccionado
        )

    registros = registros.order_by(
        "nombres_completos",
        "cedula",
    )

    total_registros = registros_base.count()
    total_filtrados = registros.count()

    con_fecha_grado = registros_base.exclude(
        fecha_grado__isnull=True
    ).count()

    pendientes_grado = registros_base.filter(
        fecha_grado__isnull=True
    ).count()

    programas = (
        registros_base
        .exclude(programa__isnull=True)
        .exclude(programa__exact="")
        .values_list("programa", flat=True)
        .distinct()
        .order_by("programa")
    )

    campo_modalidad = RegistroTitulacion._meta.get_field(
        "modalidad_titulacion"
    )

    modalidades = [
        (valor, etiqueta)
        for valor, etiqueta in campo_modalidad.choices
        if valor
    ]

    campo_estado = RegistroTitulacion._meta.get_field(
        "estado"
    )

    estados = [
        (valor, etiqueta)
        for valor, etiqueta in campo_estado.choices
        if valor
    ]

    paginador = Paginator(
        registros,
        10,
    )

    pagina = paginador.get_page(
        request.GET.get("page")
    )

    parametros = request.GET.copy()

    if "page" in parametros:
        del parametros["page"]

    contexto = {
        "registros": pagina,
        "page_obj": pagina,
        "consulta": consulta,
        "programas": programas,
        "modalidades": modalidades,
        "estados": estados,
        "programa_seleccionado": programa_seleccionado,
        "modalidad_seleccionada": modalidad_seleccionada,
        "estado_seleccionado": estado_seleccionado,
        "total_registros": total_registros,
        "total_filtrados": total_filtrados,
        "con_fecha_grado": con_fecha_grado,
        "pendientes_grado": pendientes_grado,
        "querystring": parametros.urlencode(),
    }

    return render(
        request,
        "estudiantes/lista.html",
        contexto,
    )

@login_required
def crear_registro(request):
    if request.method == "POST":
        form = RegistroTitulacionForm(
            request.POST,
            programas=opciones_programas(),
        )

        if form.is_valid():
            registro = form.save()
            guardar_programa_catalogo(registro)
            anterior = RegistroTitulacion()
            registrar_cambios(
                registro,
                anterior,
                request.user,
                accion="CREACION",
            )

            messages.success(
                request,
                "La información fue almacenada correctamente.",
            )

            return redirect(
                "estudiantes:detalle",
                pk=registro.pk,
            )
    else:
        form = RegistroTitulacionForm(programas=opciones_programas())

    contexto = {
        "form": form,
        "titulo": "Registrar información de titulación",
        "texto_boton": "Guardar toda la información",
        "secciones": construir_secciones_formulario(form),
        "programas_catalogo": form.programas_catalogo,
    }

    return render(
        request,
        "estudiantes/formulario.html",
        contexto,
    )


@login_required
@require_POST
def crear_programa(request):
    form = ProgramaForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": form.errors.get_json_data()},
            status=400,
        )

    programa = form.save(commit=False)
    programa.activo = True
    programa.save()
    return JsonResponse({
        "ok": True,
        "codigo": programa.codigo,
        "descripcion": programa.descripcion,
        "label": str(programa),
    })


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
            programas=opciones_programas(),
        )

        if form.is_valid():
            anterior = RegistroTitulacion.objects.get(pk=registro.pk)
            registro = form.save()
            guardar_programa_catalogo(registro)
            registrar_cambios(registro, anterior, request.user)

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
            programas=opciones_programas(),
        )

    contexto = {
        "form": form,
        "registro": registro,
        "titulo": "Editar información de titulación",
        "texto_boton": "Guardar cambios",
        "secciones": construir_secciones_formulario(form),
        "programas_catalogo": form.programas_catalogo,
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
def exportar_registro(request, pk):
    registro = get_object_or_404(RegistroTitulacion, pk=pk)
    contenido = exportar_registro_excel(registro)
    respuesta = HttpResponse(
        contenido,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    respuesta["Content-Disposition"] = (
        f'attachment; filename="estudiante-{registro.cedula}.xlsx"'
    )
    return respuesta


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


