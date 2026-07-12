from django import forms

from estudiantes.models import RegistroTitulacion

from .models import Acta


class ActaForm(forms.ModelForm):

    class Meta:
        model = Acta

        fields = [
            "registro",
            "tipo_acta",
            "estado",
            "observaciones",
        ]

        widgets = {
            "observaciones": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Ingrese observaciones relacionadas "
                        "con el acta."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["registro"].queryset = (
            RegistroTitulacion.objects
            .all()
            .order_by("nombres_completos")
        )

        clase = (
            "mt-1 block w-full rounded-lg border "
            "border-slate-300 bg-white px-3 py-2 "
            "shadow-sm focus:border-blue-500 "
            "focus:outline-none focus:ring-2 "
            "focus:ring-blue-200"
        )

        for campo in self.fields.values():
            campo.widget.attrs["class"] = clase

    def clean(self):
        datos = super().clean()

        registro = datos.get("registro")
        tipo_acta = datos.get("tipo_acta")

        if not registro or not tipo_acta:
            return datos

        consulta = Acta.objects.filter(
            registro=registro,
            tipo_acta=tipo_acta,
        )

        if self.instance.pk:
            consulta = consulta.exclude(
                pk=self.instance.pk
            )

        if consulta.exists():
            raise forms.ValidationError(
                "Este estudiante ya tiene un acta "
                "registrada para esa modalidad."
            )

        return datos
