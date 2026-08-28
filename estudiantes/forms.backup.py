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

    def _limpiar_nombre(self, nombre, etiqueta):
        nombre = " ".join(nombre.split())

        if not nombre:
            return nombre

        if not all(
            caracter.isalpha()
            or caracter.isspace()
            or caracter in "-'"
            for caracter in nombre
        ):
            raise forms.ValidationError(
                f"{etiqueta} solo puede contener letras, espacios, "
                "guion y apóstrofe."
            )

        return nombre

    def clean_nombres_completos(self):
        return self._limpiar_nombre(
            self.cleaned_data["nombres_completos"],
            "El nombre completo",
        )

    def clean_nombres_completos_tutor(self):
        return self._limpiar_nombre(
            self.cleaned_data["nombres_completos_tutor"],
            "El nombre del tutor",
        )


