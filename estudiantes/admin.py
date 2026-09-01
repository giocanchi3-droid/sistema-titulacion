from django.contrib import admin

from .models import HistorialExpediente, Programa, RegistroTitulacion
from .views import registrar_cambios, registrar_eliminacion


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "activo")
    list_filter = ("activo",)
    search_fields = ("codigo", "descripcion")


@admin.register(HistorialExpediente)
class HistorialExpedienteAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "registro",
        "registro_cedula",
        "responsable",
        "campo",
        "accion",
        "valor_anterior",
        "valor_nuevo",
    )
    list_filter = ("accion", "responsable")
    search_fields = (
        "registro__cedula",
        "registro__nombres_completos",
        "responsable",
        "campo",
    )
    readonly_fields = (
        "registro",
        "registro_nombre",
        "registro_cedula",
        "responsable",
        "campo",
        "valor_anterior",
        "valor_nuevo",
        "accion",
        "observacion",
        "fecha",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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

    def save_model(self, request, obj, form, change):
        anterior = None
        if change:
            anterior = RegistroTitulacion.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)
        registrar_cambios(
            obj,
            anterior or RegistroTitulacion(),
            request.user,
            accion="EDICION" if change else "CREACION",
        )

    def delete_model(self, request, obj):
        registrar_eliminacion(obj, request.user)
        super().delete_model(request, obj)
