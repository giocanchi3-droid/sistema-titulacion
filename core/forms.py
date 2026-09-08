from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


User = get_user_model()


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            usuario.set_password(password)
        if commit:
            usuario.save()
        return usuario


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