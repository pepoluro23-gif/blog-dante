from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    """Publicación del blog."""

    ESTADOS = [
        ("borrador", "Borrador"),
        ("publicado", "Publicado"),
        ("archivado", "Archivado"),
    ]

    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    contenido = models.TextField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    imagen = models.ImageField(upload_to="posts/", null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="borrador")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("detalle_post", kwargs={"slug": self.slug})

    def _generar_slug_unico(self):
        """Genera un slug a partir del título y agrega -2, -3... si ya existe."""
        base = slugify(self.titulo)[:200] or "post"
        slug = base
        contador = 2
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{contador}"
            contador += 1
        return slug

    def save(self, *args, **kwargs):
        # El slug se genera una sola vez: cambiar el título no rompe la URL.
        if not self.slug:
            self.slug = self._generar_slug_unico()
        super().save(*args, **kwargs)
