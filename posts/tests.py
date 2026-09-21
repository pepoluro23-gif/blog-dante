import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Post

MEDIA_TEMPORAL = tempfile.mkdtemp()

# GIF válido de 1x1 píxel
GIF_1PX = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00"
    b"\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class PostsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def setUp(self):
        self.ana = User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        self.beto = User.objects.create_user("beto", "beto@example.com", "clave-Segura-123")
        self.publicado = Post.objects.create(
            titulo="Post publicado", contenido="Contenido de prueba", autor=self.ana, estado="publicado"
        )
        self.borrador = Post.objects.create(
            titulo="Post borrador", contenido="Secreto", autor=self.ana, estado="borrador"
        )

    # --- Modelo ---
    def test_slug_se_genera_y_es_unico(self):
        otro = Post.objects.create(titulo="Post publicado", contenido="x", autor=self.ana)
        self.assertEqual(self.publicado.slug, "post-publicado")
        self.assertEqual(otro.slug, "post-publicado-2")

    def test_slug_no_cambia_al_editar_titulo(self):
        self.publicado.titulo = "Otro título"
        self.publicado.save()
        self.assertEqual(self.publicado.slug, "post-publicado")

    # --- Lectura pública ---
    def test_lista_solo_muestra_publicados(self):
        r = self.client.get(reverse("lista_posts"))
        self.assertContains(r, "Post publicado")
        self.assertNotContains(r, "Post borrador")

    def test_busqueda_y_sin_resultados(self):
        r = self.client.get(reverse("lista_posts"), {"q": "prueba"})
        self.assertContains(r, "Post publicado")
        r = self.client.get(reverse("lista_posts"), {"q": "zzzz"})
        self.assertContains(r, "No se encontraron posts")

    def test_detalle_publicado_es_publico(self):
        r = self.client.get(self.publicado.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_detalle_borrador_solo_para_autor(self):
        url = self.borrador.get_absolute_url()
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username="beto", password="clave-Segura-123")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username="ana", password="clave-Segura-123")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_slug_inexistente_da_404(self):
        r = self.client.get(reverse("detalle_post", args=["no-existe"]))
        self.assertEqual(r.status_code, 404)

    # --- Rutas protegidas ---
    def test_anonimo_es_redirigido_al_login(self):
        rutas = [
            reverse("crear_post"),
            reverse("mis_posts"),
            reverse("editar_post", args=[self.publicado.slug]),
            reverse("eliminar_post", args=[self.publicado.slug]),
            reverse("perfil"),
            reverse("editar_perfil"),
        ]
        for ruta in rutas:
            r = self.client.get(ruta)
            self.assertEqual(r.status_code, 302, ruta)
            self.assertTrue(r.url.startswith(reverse("login")), ruta)

    # --- CRUD ---
    def test_crear_post_con_imagen(self):
        self.client.login(username="ana", password="clave-Segura-123")
        imagen = SimpleUploadedFile("foto.gif", GIF_1PX, content_type="image/gif")
        r = self.client.post(
            reverse("crear_post"),
            {"titulo": "Nuevo con imagen", "contenido": "Hola", "estado": "publicado", "imagen": imagen},
        )
        post = Post.objects.get(titulo="Nuevo con imagen")
        self.assertRedirects(r, post.get_absolute_url())
        self.assertEqual(post.autor, self.ana)
        self.assertTrue(post.imagen.name.startswith("posts/"))

    def test_crear_post_invalido_muestra_errores(self):
        self.client.login(username="ana", password="clave-Segura-123")
        r = self.client.post(reverse("crear_post"), {"titulo": "abc", "contenido": "", "estado": "publicado"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "al menos 5 caracteres")

    def test_editar_como_autor(self):
        self.client.login(username="ana", password="clave-Segura-123")
        r = self.client.post(
            reverse("editar_post", args=[self.publicado.slug]),
            {"titulo": "Título editado", "contenido": "Nuevo", "estado": "publicado"},
        )
        self.assertRedirects(r, self.publicado.get_absolute_url())
        self.publicado.refresh_from_db()
        self.assertEqual(self.publicado.titulo, "Título editado")

    def test_otro_usuario_no_puede_editar_ni_borrar(self):
        self.client.login(username="beto", password="clave-Segura-123")
        url_editar = reverse("editar_post", args=[self.publicado.slug])
        url_borrar = reverse("eliminar_post", args=[self.publicado.slug])
        self.assertEqual(self.client.get(url_editar).status_code, 403)
        self.assertEqual(self.client.post(url_borrar).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.publicado.pk).exists())

    def test_borrado_requiere_post(self):
        self.client.login(username="ana", password="clave-Segura-123")
        url = reverse("eliminar_post", args=[self.publicado.slug])
        r = self.client.get(url)  # GET solo muestra la confirmación
        self.assertContains(r, "Sí, eliminar")
        self.assertTrue(Post.objects.filter(pk=self.publicado.pk).exists())
        self.client.post(url)
        self.assertFalse(Post.objects.filter(pk=self.publicado.pk).exists())

    def test_contacto(self):
        r = self.client.post(
            reverse("contacto"),
            {"nombre": "Luz", "email": "luz@example.com", "mensaje": "Mensaje de prueba largo"},
            follow=True,
        )
        self.assertContains(r, "Recibimos tu mensaje")
