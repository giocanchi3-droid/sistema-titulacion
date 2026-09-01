from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProgramaForm, RegistroTitulacionForm
from .models import HistorialExpediente, Programa, RegistroTitulacion
from .services_exportacion import exportar_masivo
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
                registro_nombre=registro.nombres_completos,
                registro_cedula=registro.cedula,
                responsable=responsable,
                campo=registro._meta.get_field(campo).verbose_name,
                valor_anterior=viejo,
                valor_nuevo=nuevo,
                accion=accion,
            )


def registrar_eliminacion(registro, usuario):
    responsable = getattr(usuario, "username", None) or "Sistema"
    HistorialExpediente.objects.create(
        registro=registro,
        registro_nombre=registro.nombres_completos,
        registro_cedula=registro.cedula,
        responsable=responsable,
        campo="Registro completo",
        valor_anterior=f"{registro.nombres_completos} ({registro.cedula})",
        valor_nuevo="",
        accion="ELIMINACION",
        observacion="Registro de estudiante eliminado.",
    )


def usuario_puede_auditar(usuario):
    return usuario.is_authenticated and usuario.is_staff


@user_passes_test(usuario_puede_auditar)
def auditoria(request):
    historial = HistorialExpediente.objects.all()
    filtros = {
        clave: request.GET.get(clave, "").strip()
        for clave in (
            "q", "estudiante", "cedula", "responsable", "accion",
            "campo", "fecha_desde", "fecha_hasta",
        )
    }
    if filtros["q"]:
        historial = historial.filter(
            Q(registro_nombre__icontains=filtros["q"])
            | Q(registro_cedula__icontains=filtros["q"])
            | Q(responsable__icontains=filtros["q"])
            | Q(campo__icontains=filtros["q"])
            | Q(valor_anterior__icontains=filtros["q"])
            | Q(valor_nuevo__icontains=filtros["q"])
            | Q(accion__icontains=filtros["q"])
        )
    if filtros["estudiante"]:
        historial = historial.filter(
            registro_nombre__icontains=filtros["estudiante"]
        )
    if filtros["cedula"]:
        historial = historial.filter(
            registro_cedula__icontains=filtros["cedula"]
        )
    if filtros["responsable"]:
        historial = historial.filter(
            responsable__icontains=filtros["responsable"]
        )
    if filtros["accion"]:
        historial = historial.filter(accion=filtros["accion"])
    if filtros["campo"]:
        historial = historial.filter(campo=filtros["campo"])
    fecha_desde = parse_date(filtros["fecha_desde"])
    fecha_hasta = parse_date(filtros["fecha_hasta"])
    if fecha_desde:
        historial = historial.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        historial = historial.filter(fecha__date__lte=fecha_hasta)

    pagina = Paginator(historial.order_by("-fecha"), 25).get_page(
        request.GET.get("page")
    )
    parametros = request.GET.copy()
    parametros.pop("page", None)
    return render(request, "estudiantes/auditoria.html", {
        "historial": pagina,
        "page_obj": pagina,
        "querystring": parametros.urlencode(),
        "filtros": filtros,
        "acciones": HistorialExpediente.objects.values_list(
            "accion", flat=True
        ).distinct().order_by("accion"),
        "campos": HistorialExpediente.objects.values_list(
            "campo", flat=True
        ).distinct().order_by("campo"),
    })


@user_passes_test(usuario_puede_auditar)
def historial_registro(request, pk):
    registro = get_object_or_404(RegistroTitulacion, pk=pk)
    historial = registro.historial_cambios.all().order_by("-fecha")
    pagina = Paginator(historial, 25).get_page(request.GET.get("page"))
    return render(request, "estudiantes/historial.html", {
        "registro": registro,
        "historial": pagina,
        "page_obj": pagina,
    })


@require_POST
@user_passes_test(usuario_puede_auditar)
def revertir_cambio(request, pk):
    cambio = get_object_or_404(HistorialExpediente, pk=pk)
    if cambio.registro is None or cambio.accion == "ELIMINACION":
        messages.error(request, "Este cambio no puede revertirse.")
        return redirect("estudiantes:auditoria")

    campo = next(
        (
            nombre for nombre in RegistroTitulacionForm.Meta.fields
            if RegistroTitulacion._meta.get_field(nombre).verbose_name
            == cambio.campo
        ),
        None,
    )
    if campo is None:
        messages.error(request, "El campo de este cambio no puede revertirse.")
        return redirect("estudiantes:auditoria")

    registro = cambio.registro
    anterior = RegistroTitulacion.objects.get(pk=registro.pk)
    field = RegistroTitulacion._meta.get_field(campo)
    try:
        valor = cambio.valor_anterior
        if valor == "":
            valor = None if field.null else ""
        setattr(registro, campo, valor)
        registro.full_clean()
        registro.save()
    except (TypeError, ValueError, ValidationError):
        messages.error(request, "El valor anterior no es válido para revertirlo.")
        return redirect("estudiantes:auditoria")

    registrar_cambios(registro, anterior, request.user, accion="REVERSIÓN")
    messages.success(request, "El cambio fue revertido y quedó registrado.")
    return redirect("estudiantes:historial", pk=registro.pk)


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
def buscar_estudiante(request):
    id_banner = request.GET.get("id_banner", "").strip()
    cedula = request.GET.get("cedula", "").strip()
    if not id_banner and not cedula:
        return JsonResponse({"encontrado": False})

    consulta = RegistroTitulacion.objects.all()
    if cedula:
        registro = consulta.filter(cedula=cedula).first()
    else:
        registro = consulta.filter(id_banner=id_banner).first()
    if registro is None:
        return JsonResponse({"encontrado": False})

    campos = {
        campo: getattr(registro, campo)
        for campo in RegistroTitulacionForm.Meta.fields
    }
    for campo, valor in campos.items():
        if hasattr(valor, "isoformat"):
            campos[campo] = valor.isoformat()
        elif valor is None:
            campos[campo] = ""
        else:
            campos[campo] = str(valor)
    return JsonResponse({"encontrado": True, "estudiante": campos})


@login_required
def descargar_seleccionados(request):
    if request.method != "POST":
        return redirect("estudiantes:lista")
    formato = request.POST.get("formato", "").lower()
    if formato not in {"excel", "pdf", "word"}:
        return JsonResponse({"error": "Formato no válido."}, status=400)
    ids_recibidos = request.POST.getlist("estudiante_ids")
    if any(not valor.isdigit() for valor in ids_recibidos):
        return JsonResponse({"error": "Los identificadores no son válidos."}, status=400)
    ids = set(ids_recibidos)
    registros = RegistroTitulacion.objects.filter(pk__in=ids).order_by(
        "nombres_completos", "cedula"
    )
    if len(ids) != registros.count():
        return JsonResponse({"error": "Uno o más estudiantes no existen."}, status=400)
    if not registros.exists():
        return JsonResponse({"error": "Seleccione al menos un estudiante."}, status=400)
    nombre, contenido, tipo = exportar_masivo(registros, formato)
    respuesta = HttpResponse(contenido, content_type=tipo)
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


@login_required
def eliminar_registro(request, pk):
    registro = get_object_or_404(
        RegistroTitulacion,
        pk=pk,
    )

    if request.method == "POST":
        registrar_eliminacion(registro, request.user)
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


