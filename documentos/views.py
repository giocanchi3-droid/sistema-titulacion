import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from estudiantes.models import RegistroTitulacion
from estudiantes.services_expediente import construir_requisitos

from .forms import ActaForm
from .models import Acta
from .services import generar_archivos_acta


logger = logging.getLogger(__name__)


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
def generar_acta_desde_expediente(request, registro_pk):
    """
    Crea y genera automáticamente el acta oficial
    desde el expediente digital del estudiante.
    """

    registro = get_object_or_404(
        RegistroTitulacion,
        pk=registro_pk,
    )

    if request.method != "POST":
        return redirect(
            "estudiantes:expediente",
            pk=registro.pk,
        )

    avance = construir_requisitos(registro)

    if not avance["puede_generar_acta"]:
        messages.error(
            request,
            "No se puede generar el acta porque "
            "el expediente tiene requisitos pendientes.",
        )

        return redirect(
            "estudiantes:expediente",
            pk=registro.pk,
        )

    tipo_acta = registro.modalidad_titulacion

    if tipo_acta not in dict(Acta.TIPOS_ACTA):
        messages.error(
            request,
            "El estudiante no tiene una modalidad de titulación válida.",
        )

        return redirect(
            "estudiantes:expediente",
            pk=registro.pk,
        )

    acta = Acta.objects.filter(
        registro=registro,
        tipo_acta=tipo_acta,
    ).first()

    if acta:
        messages.info(
            request,
            f"El estudiante ya tiene el acta {acta.numero_acta}.",
        )

        return redirect(
            "documentos:detalle_acta",
            pk=acta.pk,
        )

    try:
        acta = Acta.objects.create(
            registro=registro,
            tipo_acta=tipo_acta,
            estado="BORRADOR",
            creado_por=request.user,
        )

        generar_archivos_acta(acta)

        messages.success(
            request,
            f"Acta {acta.numero_acta} generada correctamente "
            "con sus documentos oficiales.",
        )

        return redirect(
            "documentos:detalle_acta",
            pk=acta.pk,
        )

    except Exception:
        logger.exception(
            "Error generando acta desde expediente %s",
            registro.pk,
        )

        if acta.pk:
            acta.delete()

        messages.error(
            request,
            "No fue posible generar el acta. "
            "Revise los datos del expediente e inténtelo nuevamente.",
        )

        return redirect(
            "estudiantes:expediente",
            pk=registro.pk,
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
def descargar_documento(request, pk, tipo):
    acta = get_object_or_404(Acta, pk=pk)
    campos = {
        "word": ("archivo_word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "pdf": ("archivo_pdf", "application/pdf"),
    }

    if tipo not in campos:
        raise Http404("Tipo de documento no vÃ¡lido.")

    campo, content_type = campos[tipo]
    archivo = getattr(acta, campo)

    if not archivo:
        raise Http404("El documento todavÃ­a no ha sido generado.")

    try:
        url = archivo.url
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("El documento no existe en el almacenamiento configurado.")

    return HttpResponseRedirect(url)


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

# GESTION_ACTAS_SAFE_START

import unicodedata as _ga_unicodedata

from django.contrib.auth.decorators import (
    login_required as _ga_login_required,
)
from django.shortcuts import render as _ga_render
from django.urls import (
    NoReverseMatch as _ga_NoReverseMatch,
)
from django.urls import reverse as _ga_reverse
from django.utils.text import slugify as _ga_slugify

from .models import Acta as _GAActa


def _ga_safe_value(objeto, *rutas):
    """
    Obtiene el primer atributo disponible sin provocar
    VariableDoesNotExist ni AttributeError.
    """

    for ruta in rutas:
        actual = objeto

        try:
            for parte in ruta.split("."):
                actual = getattr(actual, parte)

                if callable(actual):
                    actual = actual()

            if actual is not None and actual != "":
                return actual

        except Exception:
            continue

    return ""


def _ga_normalize(valor):
    texto = str(valor or "").strip().lower()

    texto = _ga_unicodedata.normalize(
        "NFD",
        texto,
    )

    return "".join(
        caracter
        for caracter in texto
        if _ga_unicodedata.category(caracter) != "Mn"
    )


def _ga_file_url(objeto, *rutas):
    archivo = _ga_safe_value(
        objeto,
        *rutas,
    )

    if not archivo:
        return ""

    try:
        return archivo.url
    except Exception:
        return ""


def _ga_reverse_first(nombres, pk=None):
    for nombre in nombres:
        ruta = f"documentos:{nombre}"

        try:
            if pk is None:
                return _ga_reverse(ruta)

            return _ga_reverse(
                ruta,
                args=[pk],
            )

        except _ga_NoReverseMatch:
            try:
                if pk is not None:
                    return _ga_reverse(
                        ruta,
                        kwargs={"pk": pk},
                    )
            except _ga_NoReverseMatch:
                pass

    return ""


def _ga_format_date(valor):
    if not valor:
        return "", ""

    try:
        fecha = valor.strftime("%d/%m/%Y")
    except Exception:
        fecha = str(valor)

    try:
        hora = valor.strftime("%H:%M")
    except Exception:
        hora = ""

    return fecha, hora


def _ga_build_row(acta):
    codigo = _ga_safe_value(
        acta,
        "numero_acta",
        "codigo",
        "numero",
        "id",
    )

    estudiante = _ga_safe_value(
        acta,
        "registro.nombres_completos",
        "estudiante.nombres_completos",
        "nombre_estudiante",
        "registro.nombre",
        "estudiante.nombre",
    )

    cedula = _ga_safe_value(
        acta,
        "registro.cedula",
        "estudiante.cedula",
        "cedula",
    )

    programa = _ga_safe_value(
        acta,
        "registro.programa",
        "estudiante.programa",
        "programa",
    )

    tipo = _ga_safe_value(
        acta,
        "get_tipo_acta_display",
        "get_tipo_display",
        "tipo_acta",
        "tipo",
    )

    estado = _ga_safe_value(
        acta,
        "get_estado_display",
        "estado",
    )

    estado_original = _ga_safe_value(
        acta,
        "estado",
    )

    fecha_valor = _ga_safe_value(
        acta,
        "fecha_generacion",
        "fecha_creacion",
        "creado_en",
        "created_at",
    )

    fecha, hora = _ga_format_date(
        fecha_valor
    )

    estudiante_texto = (
        str(estudiante).strip()
        if estudiante
        else "No registrado"
    )

    estado_texto = (
        str(estado).strip()
        if estado
        else "Generada"
    )

    tipo_texto = (
        str(tipo).strip()
        if tipo
        else "Acta de titulaciÃ³n"
    )

    codigo_texto = (
        str(codigo).strip()
        if codigo
        else f"ACTA-{acta.pk}"
    )

    return {
        "pk": acta.pk,
        "codigo": codigo_texto,
        "estudiante": estudiante_texto,
        "inicial": estudiante_texto[:1].upper(),
        "cedula": (
            str(cedula).strip()
            if cedula
            else "No registrada"
        ),
        "programa": (
            str(programa).strip()
            if programa
            else "No registrado"
        ),
        "tipo": tipo_texto,
        "estado": estado_texto,
        "estado_original": str(
            estado_original or estado_texto
        ),
        "estado_normalizado": _ga_normalize(
            estado_texto
        ),
        "estado_clase": (
            _ga_slugify(estado_texto)
            or "generada"
        ),
        "fecha": fecha,
        "hora": hora,
        "url_detalle": _ga_reverse_first(
            [
                "detalle_acta",
                "acta_detalle",
                "detalle",
            ],
            acta.pk,
        ),
        "url_editar": _ga_reverse_first(
            [
                "editar_acta",
                "acta_editar",
                "editar",
            ],
            acta.pk,
        ),
        "url_generar": _ga_reverse_first(
            [
                "generar_oficial_prioridad",
                "generar_documentos",
                "generar_acta",
                "regenerar_acta",
            ],
            acta.pk,
        ),
        "url_word": _ga_file_url(
            acta,
            "archivo_word",
            "documento_word",
            "word",
        ),
        "url_pdf": _ga_file_url(
            acta,
            "archivo_pdf",
            "documento_pdf",
            "pdf",
        ),
    }


@_ga_login_required
def lista_actas(request):
    consulta = request.GET.get(
        "q",
        "",
    ).strip()

    estado_seleccionado = request.GET.get(
        "estado",
        "",
    ).strip()

    queryset = _GAActa.objects.all()

    try:
        queryset = queryset.order_by("-pk")
    except Exception:
        pass

    filas_completas = [
        _ga_build_row(acta)
        for acta in queryset
    ]

    estados_disponibles = {}

    for fila in filas_completas:
        valor = fila["estado_original"]
        etiqueta = fila["estado"]

        if valor:
            estados_disponibles[str(valor)] = etiqueta

    filas_filtradas = []

    consulta_normalizada = _ga_normalize(
        consulta
    )

    estado_normalizado = _ga_normalize(
        estado_seleccionado
    )

    for fila in filas_completas:
        texto_busqueda = _ga_normalize(
            " ".join(
                [
                    fila["codigo"],
                    fila["estudiante"],
                    fila["cedula"],
                    fila["programa"],
                    fila["tipo"],
                    fila["estado"],
                ]
            )
        )

        coincide_busqueda = (
            not consulta_normalizada
            or consulta_normalizada in texto_busqueda
        )

        estado_fila_original = _ga_normalize(
            fila["estado_original"]
        )

        coincide_estado = (
            not estado_normalizado
            or estado_normalizado
            in {
                estado_fila_original,
                fila["estado_normalizado"],
            }
        )

        if coincide_busqueda and coincide_estado:
            filas_filtradas.append(fila)

    total_generadas = sum(
        1
        for fila in filas_filtradas
        if (
            "generad" in fila["estado_normalizado"]
            or "emitid" in fila["estado_normalizado"]
        )
    )

    total_aprobadas = sum(
        1
        for fila in filas_filtradas
        if (
            "aprobad" in fila["estado_normalizado"]
            or "validad" in fila["estado_normalizado"]
        )
    )

    total_anuladas = sum(
        1
        for fila in filas_filtradas
        if (
            "anulad" in fila["estado_normalizado"]
            or "cancelad" in fila["estado_normalizado"]
        )
    )

    contexto = {
        "filas_actas": filas_filtradas,
        "consulta": consulta,
        "estado_seleccionado": estado_seleccionado,
        "estados": sorted(
            estados_disponibles.items(),
            key=lambda item: item[1],
        ),
        "total_actas": len(filas_filtradas),
        "total_generadas": total_generadas,
        "total_aprobadas": total_aprobadas,
        "total_anuladas": total_anuladas,
        "lista_url": request.path,
        "crear_url": _ga_reverse_first(
            [
                "crear_acta",
                "nueva_acta",
                "seleccionar_estudiante",
                "generar",
            ]
        ),
    }

    return _ga_render(
        request,
        "documentos/lista_actas.html",
        contexto,
    )


# GESTION_ACTAS_SAFE_END


# === PUCETEC ACTAS OFICIALES START ===

@login_required
def vista_previa_acta(request, pk):
    from django.shortcuts import get_object_or_404, render

    from .models import Acta
    from .acta_documentos import contexto_acta

    acta = get_object_or_404(
        Acta.objects.select_related("registro"),
        pk=pk,
    )

    contexto = contexto_acta(acta)

    return render(
        request,
        "documentos/vista_previa_acta.html",
        contexto,
    )


@login_required
def generar_documentos_oficiales(request, pk):
    from django.contrib import messages
    from django.conf import settings
    from django.core.files.base import ContentFile
    from django.shortcuts import get_object_or_404, redirect
    from django.utils import timezone
    from django.utils.text import slugify

    from .models import Acta
    from .acta_documentos import (
        generar_pdf_oficial,
        generar_word_oficial,
    )

    if request.method != "POST":
        return redirect(
            "documentos:vista_previa_acta",
            pk=pk,
        )

    acta = get_object_or_404(
        Acta.objects.select_related("registro"),
        pk=pk,
    )

    logo_path = (
        settings.BASE_DIR
        / "static"
        / "img"
        / "logo-pucetec-actas.jpg"
    )

    if not logo_path.exists():
        messages.error(
            request,
            "No se encontro el logo PUCE TEC.",
        )

        return redirect(
            "documentos:vista_previa_acta",
            pk=pk,
        )

    try:
        contenido_word = generar_word_oficial(
            acta,
            logo_path,
        )

        contenido_pdf = generar_pdf_oficial(
            acta,
            logo_path,
        )

        nombre_base = slugify(
            acta.numero_acta
            or f"acta-{acta.pk}"
        )

        if not nombre_base:
            nombre_base = f"acta-{acta.pk}"

        acta.archivo_word.save(
            f"{nombre_base}.docx",
            ContentFile(contenido_word),
            save=False,
        )

        acta.archivo_pdf.save(
            f"{nombre_base}.pdf",
            ContentFile(contenido_pdf),
            save=False,
        )

        acta.fecha_generacion = timezone.now()

        campos = [
            "archivo_word",
            "archivo_pdf",
            "fecha_generacion",
        ]

        if acta.estado == Acta.ESTADOS[0][0]:
            acta.estado = Acta.ESTADOS[1][0]
            campos.append("estado")

        acta.save(
            update_fields=campos
        )

        messages.success(
            request,
            "Acta PUCE TEC generada correctamente "
            "en Word y PDF.",
        )

    except Exception as exc:
        logger.exception(
            "Error al generar documentos oficiales para el acta %s",
            acta.pk,
        )
        messages.error(
            request,
            "No fue posible generar el acta. "
            "Verifique los datos e intÃ©ntelo nuevamente.",
        )

    return redirect(
        "documentos:vista_previa_acta",
        pk=acta.pk,
    )

# === PUCETEC ACTAS OFICIALES END ===

# === GENERACION OFICIAL PUCETEC START ===

@login_required
def generar_documentos(request, pk):

    from django.conf import settings
    from django.contrib import messages
    from django.core.files.base import ContentFile
    from django.shortcuts import get_object_or_404, redirect
    from django.utils import timezone
    from django.utils.text import slugify

    from .models import Acta

    from .generador_actas_oficial import (
        generar_pdf_oficial,
        generar_word_oficial,
    )

    if request.method != "POST":
        return redirect(
            "documentos:detalle_acta",
            pk=pk,
        )

    acta = get_object_or_404(
        Acta.objects.select_related(
            "registro"
        ),
        pk=pk,
    )

    logo = (
        settings.BASE_DIR
        / "static"
        / "img"
        / "logo-pucetec-actas.png"
    )

    if not logo.exists():
        messages.error(
            request,
            "No se encontr? el logo PUCE TEC.",
        )

        return redirect(
            "documentos:detalle_acta",
            pk=acta.pk,
        )

    try:

        word = generar_word_oficial(
            acta,
            logo,
        )

        pdf = generar_pdf_oficial(
            acta,
            logo,
        )

        nombre = slugify(
            acta.numero_acta
            or f"acta-{acta.pk}"
        )

        if not nombre:
            nombre = f"acta-{acta.pk}"

        # Eliminar documentos antiguos para no
        # seguir descargando el formato anterior.

        if acta.archivo_word:
            acta.archivo_word.delete(
                save=False
            )

        if acta.archivo_pdf:
            acta.archivo_pdf.delete(
                save=False
            )

        acta.archivo_word.save(
            f"{nombre}.docx",
            ContentFile(word),
            save=False,
        )

        acta.archivo_pdf.save(
            f"{nombre}.pdf",
            ContentFile(pdf),
            save=False,
        )

        acta.fecha_generacion = (
            timezone.now()
        )

        campos = [
            "archivo_word",
            "archivo_pdf",
            "fecha_generacion",
        ]

        if acta.estado == Acta.ESTADOS[0][0]:
            acta.estado = Acta.ESTADOS[1][0]
            campos.append("estado")

        acta.save(
            update_fields=campos
        )

        messages.success(
            request,
            "El Word y PDF fueron regenerados "
            "con el formato oficial PUCE TEC.",
        )

    except Exception as error:
        logger.exception(
            "Error al regenerar documentos oficiales para el acta %s",
            acta.pk,
        )

        messages.error(
            request,
            "No fue posible generar los documentos. "
            "Verifique los datos e intÃ©ntelo nuevamente.",
        )

    return redirect(
        "documentos:detalle_acta",
        pk=acta.pk,
    )

# === GENERACION OFICIAL PUCETEC END ===




