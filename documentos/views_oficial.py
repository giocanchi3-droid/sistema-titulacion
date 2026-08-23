import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify

from .models import Acta
from .acta_formato_oficial import (
    crear_pdf,
    crear_word,
)


logger = logging.getLogger(__name__)


@login_required
def generar_oficial(request, pk):

    acta = get_object_or_404(
        Acta.objects.select_related(
            "registro"
        ),
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "documentos:detalle_acta",
            pk=pk
        )

    logo = (
        settings.BASE_DIR
        / "static"
        / "img"
        / "logo-pucetec-oficial.png"
    )

    if not logo.exists():
        messages.error(
            request,
            "No se encontró el logo PUCE TEC."
        )

        return redirect(
            "documentos:detalle_acta",
            pk=pk
        )

    try:
        pdf = crear_pdf(
            acta,
            logo
        )

        word = crear_word(
            acta,
            logo
        )

        nombre = slugify(
            acta.numero_acta
            or f"acta-{acta.pk}"
        )

        # BORRAR DEFINITIVAMENTE LOS DOCUMENTOS ANTIGUOS

        if acta.archivo_pdf:
            try:
                acta.archivo_pdf.delete(
                    save=False
                )
            except Exception:
                pass

        if acta.archivo_word:
            try:
                acta.archivo_word.delete(
                    save=False
                )
            except Exception:
                pass

        # Nombre diferente para evitar cache del navegador

        acta.archivo_pdf.save(
            f"{nombre}-PUCETEC-OFICIAL.pdf",
            ContentFile(pdf),
            save=False
        )

        acta.archivo_word.save(
            f"{nombre}-PUCETEC-OFICIAL.docx",
            ContentFile(word),
            save=False
        )

        acta.fecha_generacion = (
            timezone.now()
        )

        if acta.estado == Acta.ESTADOS[0][0]:
            acta.estado = Acta.ESTADOS[1][0]

        acta.save()

        messages.success(
            request,
            "Acta regenerada con el formato "
            "oficial PUCE TEC."
        )

    except Exception as error:
        logger.exception(
            "Error al generar el acta oficial %s",
            acta.pk,
        )
        messages.error(
            request,
            "No fue posible generar el acta. "
            "Verifique los datos e inténtelo nuevamente."
        )

    return redirect(
        "documentos:detalle_acta",
        pk=pk
    )
