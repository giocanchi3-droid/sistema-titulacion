from django import forms

from .models import RegistroTitulacion


class RegistroTitulacionForm(forms.ModelForm):

    class Meta:
        model = RegistroTitulacion

        fields = [
            "id_banner",
            "nombres_completos",
            "cedula",
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
            "tema": forms.Textarea(
                attrs={"rows": 4}
            ),
            "observacion_puce_tec": forms.Textarea(
                attrs={"rows": 4}
            ),
            "observaciones_secretaria_general": forms.Textarea(
                attrs={"rows": 4}
            ),
            "nueva_observacion_puce_tec": forms.Textarea(
                attrs={"rows": 4}
            ),
            "observacion_secretaria": forms.Textarea(
                attrs={"rows": 4}
            ),
            "fecha_grado": forms.DateInput(
                attrs={"type": "date"}
            ),
            "proyecto_escrito": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
            "defensa_oral": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
            "nota_final": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
            "examen_teorico_complexivo": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
            "examen_teorico_practico": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
            "nota_final2": forms.NumberInput(
                attrs={
                    "min": "0",
                    "max": "10",
                    "step": "0.01",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        clase_general = (
            "mt-1 block w-full rounded-lg border "
            "border-slate-300 bg-white px-3 py-2 "
            "shadow-sm focus:border-blue-500 "
            "focus:outline-none focus:ring-2 "
            "focus:ring-blue-200"
        )

        for field in self.fields.values():
            field.widget.attrs["class"] = clase_general

        self.fields["cedula"].widget.attrs.update(
            {
                "maxlength": "10",
                "minlength": "10",
                "inputmode": "numeric",
                "placeholder": "10 dígitos",
            }
        )

        self.fields["celular"].widget.attrs.update(
            {
                "inputmode": "numeric",
                "placeholder": "Ejemplo: 0987654321",
            }
        )

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()

        if not cedula.isdigit():
            raise forms.ValidationError(
                "La cédula solo puede contener números."
            )

        if len(cedula) != 10:
            raise forms.ValidationError(
                "La cédula debe contener exactamente 10 dígitos."
            )

        return cedula
