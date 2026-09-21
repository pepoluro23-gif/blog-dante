import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Perfil

MEDIA_TEMPORAL = tempfile.mkdtemp()

GIF_1PX = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00"
    b"\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)

DATOS_REGISTRO = {
    "username": "nuevo",
    "email": "nuevo@example.com",
    "first_name": "Nuevo",
    "last_name": "Usuario",
    "password1": "clave-Segura-123",
    "password2": "clave-Segura-123",
}


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class AccountsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def test_registro_crea_usuario_y_perfil(self):
        r = self.client.post(reverse("registro"), DATOS_REGISTRO)
        self.assertRedirects(r, reverse("login"))
        usuario = User.objects.get(username="nuevo")
        self.assertTrue(Perfil.objects.filter(user=usuario).exists())
        self.assertNotEqual(usuario.password, "clave-Segura-123")  # se guarda hasheada

    def test_registro_rechaza_email_repetido(self):
        User.objects.create_user("otro", "nuevo@example.com", "clave-Segura-123")
        r = self.client.post(reverse("registro"), DATOS_REGISTRO)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ya existe una cuenta con ese correo")

    def test_registro_rechaza_passwords_distintas(self):
        datos = dict(DATOS_REGISTRO, password2="otra-clave-456")
        r = self.client.post(reverse("registro"), datos)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="nuevo").exists())

    def test_login_y_logout(self):
        User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        r = self.client.post(reverse("login"), {"username": "ana", "password": "clave-Segura-123"})
        self.assertRedirects(r, reverse("lista_posts"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_por_get_no_esta_permitido(self):
        User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        self.client.login(username="ana", password="clave-Segura-123")
        r = self.client.get(reverse("logout"))
        self.assertEqual(r.status_code, 405)

    def test_login_incorrecto(self):
        r = self.client.post(reverse("login"), {"username": "x", "password": "y"})
        self.assertContains(r, "incorrectos")

    def test_editar_perfil_con_avatar(self):
        User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        self.client.login(username="ana", password="clave-Segura-123")
        avatar = SimpleUploadedFile("a.gif", GIF_1PX, content_type="image/gif")
        r = self.client.post(
            reverse("editar_perfil"),
            {"biografia": "Hola", "link_web": "https://example.com", "avatar": avatar},
        )
        self.assertRedirects(r, reverse("perfil"))
        perfil = Perfil.objects.get(user__username="ana")
        self.assertEqual(perfil.biografia, "Hola")
        self.assertTrue(perfil.avatar.name.startswith("avatares/"))

    def test_perfil_sin_avatar_no_rompe(self):
        User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        self.client.login(username="ana", password="clave-Segura-123")
        self.assertEqual(self.client.get(reverse("perfil")).status_code, 200)

    def test_cambio_de_password(self):
        User.objects.create_user("ana", "ana@example.com", "clave-Segura-123")
        self.client.login(username="ana", password="clave-Segura-123")
        r = self.client.post(
            reverse("password_change"),
            {
                "old_password": "clave-Segura-123",
                "new_password1": "otra-Clave-Nueva-456",
                "new_password2": "otra-Clave-Nueva-456",
            },
        )
        self.assertRedirects(r, reverse("perfil"))
        self.assertTrue(User.objects.get(username="ana").check_password("otra-Clave-Nueva-456"))
