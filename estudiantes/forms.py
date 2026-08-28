from django import forms
from .models import Programa, RegistroTitulacion


class RegistroTitulacionForm(forms.ModelForm):

    def __init__(self, *args, programas=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.programas_catalogo = list(
            programas if programas is not None
            else Programa.objects.filter(activo=True)
        )
        self.fields["programa"].widget = forms.Select(
            choices=[
                (programa.codigo, str(programa))
                for programa in self.programas_catalogo
            ],
            attrs={"class": "form-control", "data-programa-select": "true"},
        )
        self.fields["programa_desc"].widget.attrs.update({
            "readonly": "readonly",
            "data-programa-description": "true",
        })

    def clean_programa(self):
        codigo = self.cleaned_data["programa"].strip().upper()
        programa = Programa.objects.filter(
            codigo=codigo,
            activo=True,
        ).first()
        if programa is None:
            raise forms.ValidationError(
                "Seleccione un programa activo del catálogo."
            )
        return programa.codigo

    def clean(self):
        cleaned_data = super().clean()
        codigo = cleaned_data.get("programa")
        if codigo:
            programa = Programa.objects.get(codigo=codigo, activo=True)
            cleaned_data["programa_desc"] = programa.descripcion
        return cleaned_data

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


class ProgramaForm(forms.ModelForm):

    class Meta:
        model = Programa
        fields = ["codigo", "descripcion"]

    def clean_codigo(self):
        codigo = " ".join(self.cleaned_data["codigo"].upper().split())
        if Programa.objects.filter(codigo=codigo).exists():
            raise forms.ValidationError(
                "Ya existe un programa con ese código."
            )
        return codigo

    def clean_descripcion(self):
        descripcion = " ".join(self.cleaned_data["descripcion"].split())
        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")
        return descripcion
