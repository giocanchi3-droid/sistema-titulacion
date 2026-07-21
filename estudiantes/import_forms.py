from django import forms


class ImportarExcelForm(forms.Form):

    archivo = forms.FileField(
        label="Archivo Excel",
        help_text=(
            "Seleccione la matriz institucional en formato .xlsx. "
            "El tamaño máximo permitido es de 10 MB."
        ),
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".xlsx",
                "class": (
                    "mt-1 block w-full rounded-lg border "
                    "border-slate-300 bg-white px-3 py-2 "
                    "shadow-sm focus:border-blue-500 "
                    "focus:outline-none focus:ring-2 "
                    "focus:ring-blue-200"
                ),
            }
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]

        if not archivo.name.lower().endswith(".xlsx"):
            raise forms.ValidationError(
                "El archivo debe estar en formato .xlsx."
            )

        limite = 10 * 1024 * 1024

        if archivo.size > limite:
            raise forms.ValidationError(
                "El archivo no puede superar los 10 MB."
            )

        return archivo
