from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if not username:
            raise forms.ValidationError(
                "Ingresa un nombre de usuario."
            )

        if len(username) < 3:
            raise forms.ValidationError(
                "El nombre de usuario debe tener al menos 3 caracteres."
            )

        if not all(
            caracter.isalnum() or caracter in "._-"
            for caracter in username
        ):
            raise forms.ValidationError(
                "El usuario solo puede contener letras, números, punto, "
                "guion y guion bajo."
            )

        return username