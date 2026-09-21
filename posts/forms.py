from django import forms

from .models import Post

MAX_IMAGEN_MB = 3


class PostForm(forms.ModelForm):
    """Formulario para crear y editar posts. El autor lo asigna la vista."""

    class Meta:
        model = Post
        fields = ["titulo", "subtitulo", "contenido", "estado", "imagen"]
        labels = {
            "titulo": "Título",
            "subtitulo": "Subtítulo (opcional)",
            "contenido": "Contenido",
            "estado": "Estado",
            "imagen": "Imagen destacada (opcional)",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "subtitulo": forms.TextInput(attrs={"class": "form-control"}),
            "contenido": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        return titulo

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        # Solo validamos archivos nuevos (los ya guardados no tienen content_type)
        if imagen and hasattr(imagen, "content_type"):
            if not imagen.content_type.startswith("image/"):
                raise forms.ValidationError("El archivo debe ser una imagen.")
            if imagen.size > MAX_IMAGEN_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"La imagen no puede pesar más de {MAX_IMAGEN_MB} MB."
                )
        return imagen


class ContactoForm(forms.Form):
    """Formulario independiente (forms.Form): no está ligado a ningún modelo."""

    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    mensaje = forms.CharField(
        min_length=10,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}),
    )
