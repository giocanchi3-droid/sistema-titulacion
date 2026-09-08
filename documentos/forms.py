from django import forms

from core.permissions import allowed_edit_fields
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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.allowed_fields = (
            allowed_edit_fields(user, Acta)
            if user else set(self.fields)
        )
        if user and not user.is_superuser:
            for name in list(self.fields):
                if name not in self.allowed_fields:
                    del self.fields[name]

        if not self.instance.pk:
            self.fields["estado"].initial = "BORRADOR"
            self.fields["estado"].required = False

        if "registro" in self.fields:
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
        if self.user and not self.user.is_superuser:
            submitted = set(self.data) & set(self.Meta.fields)
            if submitted - self.allowed_fields:
                raise forms.ValidationError(
                    "No tiene permiso para modificar esos campos."
                )

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
