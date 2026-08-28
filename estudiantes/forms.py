from django import forms
from .models import RegistroTitulacion


class RegistroTitulacionForm(forms.ModelForm):

    def __init__(self, *args, programas=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.programas_catalogo = list(programas or [])

        for nombre in ("programa", "programa_desc"):
            self.fields[nombre].widget.attrs["list"] = (
                f"opciones-{nombre}"
            )

    class Meta:
        model = RegistroTitulacion

        fields = [
            "id_banner",
            "cedula",
            "nombres_completos",
            "celular",
            "correo_personal",
            "correo_instituc",
            "sede",
            "programa",
            "programa_desc",
            "numero_cohorte",
            "periodo_ingreso",
            "nivel2",
            "modalidad_titulacion",
            "matricula_uic",
            "periodo_titulacion_senescyt",
            "estado",
            "cumplimiento_idioma",
            "materia_practicas_pre_profesionales",
            "horas_240",
            "materia_servicio_comunitario",
            "horas_120",
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
            "proyecto_escrito",
            "defensa_oral",
            "nota_final",
            "examen_teorico_complexivo",
            "examen_teorico_practico",
            "nota_final2",
            "observacion_puce_tec",
            "observaciones_secretaria_general",
            "nueva_observacion_puce_tec",
            "estado_envio_registro",
            "fecha_grado",
            "observacion_secretaria",
        ]

        widgets = {
            "id_banner": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su ID Banner",
            }),

            "cedula": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese su cédula",
            }),

            "nombres_completos": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombres completos",
            }),

            "celular": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de celular",
            }),

            "correo_personal": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo personal",
            }),

            "correo_instituc": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo institucional",
            }),

            "sede": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Sede",
            }),

            "programa": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Programa",
            }),

            "programa_desc": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Descripción del programa",
            }),

            "tema": forms.Textarea(attrs={"rows": 4}),
            "observacion_puce_tec": forms.Textarea(attrs={"rows": 4}),
            "observaciones_secretaria_general": forms.Textarea(attrs={"rows": 4}),
            "nueva_observacion_puce_tec": forms.Textarea(attrs={"rows": 4}),
            "observacion_secretaria": forms.Textarea(attrs={"rows": 4}),
            "fecha_grado": forms.DateInput(attrs={"type": "date"}),
            "proyecto_escrito": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "defensa_oral": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "nota_final": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "examen_teorico_complexivo": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "examen_teorico_practico": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
            "nota_final2": forms.NumberInput(attrs={"min": "0", "max": "10", "step": "0.01"}),
        }
