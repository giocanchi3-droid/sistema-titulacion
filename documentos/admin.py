from django.contrib import admin

from .models import Acta


@admin.register(Acta)
class ActaAdmin(admin.ModelAdmin):

    list_display = (
        "numero_acta",
        "registro",
        "tipo_acta",
        "estado",
        "creado_por",
        "fecha_generacion",
        "fecha_actualizacion",
    )

    list_filter = (
        "tipo_acta",
        "estado",
        "fecha_creacion",
    )

    search_fields = (
        "numero_acta",
        "registro__cedula",
        "registro__nombres_completos",
        "registro__programa",
    )

    readonly_fields = (
        "numero_acta",
        "archivo_word",
        "archivo_pdf",
        "fecha_creacion",
        "fecha_generacion",
        "fecha_actualizacion",
    )
