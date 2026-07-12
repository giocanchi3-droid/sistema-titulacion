from django.conf import settings
from django.db import models
from django.utils import timezone

from estudiantes.models import RegistroTitulacion


def ruta_acta_word(instance, filename):
    return (
        f"actas/{instance.registro.cedula}/word/"
        f"{filename}"
    )


def ruta_acta_pdf(instance, filename):
    return (
        f"actas/{instance.registro.cedula}/pdf/"
        f"{filename}"
    )


class Acta(models.Model):

    TIPOS_ACTA = [
        (
            "TRABAJO_ESCRITO",
            "Acta de titulación por trabajo escrito",
        ),
        (
            "EXAMEN_COMPLEXIVO",
            "Acta de titulación por examen complexivo",
        ),
    ]

    ESTADOS = [
        ("BORRADOR", "Borrador"),
        ("GENERADA", "Generada"),
        ("REVISION", "En revisión"),
        ("APROBADA", "Aprobada"),
        ("ANULADA", "Anulada"),
    ]

    registro = models.ForeignKey(
        RegistroTitulacion,
        on_delete=models.CASCADE,
        related_name="actas",
        verbose_name="Estudiante",
    )

    numero_acta = models.CharField(
        "Número de acta",
        max_length=30,
        unique=True,
        blank=True,
    )

    tipo_acta = models.CharField(
        "Tipo de acta",
        max_length=30,
        choices=TIPOS_ACTA,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="BORRADOR",
    )

    observaciones = models.TextField(
        blank=True,
    )

    archivo_word = models.FileField(
        upload_to=ruta_acta_word,
        blank=True,
    )

    archivo_pdf = models.FileField(
        upload_to=ruta_acta_pdf,
        blank=True,
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actas_creadas",
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_generacion = models.DateTimeField(
        null=True,
        blank=True,
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-fecha_actualizacion"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "registro",
                    "tipo_acta",
                ],
                name="acta_unica_por_estudiante_y_tipo",
            )
        ]

        verbose_name = "Acta"
        verbose_name_plural = "Actas"

    def generar_numero_acta(self):
        anio = timezone.localdate().year
        prefijo = f"ACTA-{anio}-"

        ultima_acta = (
            Acta.objects
            .filter(numero_acta__startswith=prefijo)
            .order_by("-numero_acta")
            .first()
        )

        siguiente = 1

        if ultima_acta:
            try:
                siguiente = (
                    int(
                        ultima_acta.numero_acta.split("-")[-1]
                    )
                    + 1
                )
            except (TypeError, ValueError):
                siguiente = Acta.objects.filter(
                    numero_acta__startswith=prefijo
                ).count() + 1

        return f"{prefijo}{siguiente:04d}"

    def save(self, *args, **kwargs):
        if not self.numero_acta:
            self.numero_acta = self.generar_numero_acta()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.numero_acta} - "
            f"{self.registro.nombres_completos}"
        )
