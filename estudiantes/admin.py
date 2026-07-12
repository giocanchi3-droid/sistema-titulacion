from django.contrib import admin

from .models import RegistroTitulacion


@admin.register(RegistroTitulacion)
class RegistroTitulacionAdmin(admin.ModelAdmin):

    list_display = (
        "cedula",
        "nombres_completos",
        "id_banner",
        "programa",
        "modalidad_titulacion",
        "estado",
        "fecha_grado",
    )

    list_filter = (
        "programa",
        "modalidad_titulacion",
        "estado",
        "sede",
        "cumplimiento_idioma",
    )

    search_fields = (
        "cedula",
        "nombres_completos",
        "id_banner",
        "programa",
        "nombres_completos_tutor",
        "tema",
    )

    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )

    fieldsets = (
        (
            "Información personal",
            {
                "fields": (
                    "id_banner",
                    "nombres_completos",
                    "cedula",
                    "celular",
                    "correo_personal",
                    "correo_instituc",
                    "sede",
                    "programa",
                    "programa_desc",
                )
            },
        ),
        (
            "Información académica",
            {
                "fields": (
                    "numero_cohorte",
                    "periodo_ingreso",
                    "nivel2",
                    "modalidad_titulacion",
                    "matricula_uic",
                    "periodo_titulacion_senescyt",
                    "estado",
                    "cumplimiento_idioma",
                )
            },
        ),
        (
            "Prácticas y servicio comunitario",
            {
                "fields": (
                    "materia_practicas_pre_profesionales",
                    "horas_240",
                    "materia_servicio_comunitario",
                    "horas_120",
                )
            },
        ),
        (
            "Tutor, tema y tribunal",
            {
                "fields": (
                    "nombres_completos_tutor",
                    "id_tutor",
                    "tema",
                    "primer_miembro_tribunal",
                    "primer_miembro_id_docente",
                    "segundo_miembro_tribunal",
                    "segundo_miembro_id_docente",
                    "tercer_miembro_tribunal",
                    "tercer_miembro_id_docente",
                    "cuarto_miembro_tribunal",
                    "cuarto_miembro_id_docente",
                )
            },
        ),
        (
            "Calificaciones",
            {
                "fields": (
                    "proyecto_escrito",
                    "defensa_oral",
                    "nota_final",
                    "examen_teorico_complexivo",
                    "examen_teorico_practico",
                    "nota_final2",
                )
            },
        ),
        (
            "Observaciones y grado",
            {
                "fields": (
                    "observacion_puce_tec",
                    "observaciones_secretaria_general",
                    "nueva_observacion_puce_tec",
                    "estado_envio_registro",
                    "fecha_grado",
                    "observacion_secretaria",
                    "fecha_creacion",
                    "fecha_actualizacion",
                )
            },
        ),
    )
