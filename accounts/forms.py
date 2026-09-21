from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name")
        labels = {"first_name": "Nombre", "last_name": "Apellido"}

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "form-control")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["biografia", "link_web", "avatar"]
        labels = {
            "biografia": "Biografía",
            "link_web": "Sitio web",
            "avatar": "Avatar",
        }
        widgets = {
            "biografia": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "link_web": forms.URLInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "content_type"):
            if not avatar.content_type.startswith("image/"):
                raise forms.ValidationError("El archivo debe ser una imagen.")
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("El avatar no puede pesar más de 2 MB.")
        return avatar
