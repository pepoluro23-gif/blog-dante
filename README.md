# Blog de Dante

Blog personal sobre datos, Python y servicios, desarrollado con Django como proyecto final del curso de Python de Coderhouse.

## Descripción

Aplicación web donde los usuarios registrados pueden crear, editar y eliminar posts (con imagen), y cualquier visitante puede leer los posts publicados, buscarlos y navegarlos con paginación. Incluye registro, login, logout y perfil de usuario con avatar.

## Tecnologías

- Python 3.10+
- Django 5.2
- Bootstrap 5 (tema [Clean Blog](https://startbootstrap.com/theme/clean-blog) de Start Bootstrap, licencia MIT)
- SQLite
- Pillow (manejo de imágenes)
- python-decouple (variables de entorno)

## Funcionalidades

- CRUD completo de posts desde la web (crear, ver, editar, eliminar), con imagen opcional.
- Estados de post: borrador, publicado y archivado. Los no publicados solo los ven su autor y el staff.
- Búsqueda por texto (título, subtítulo y contenido) y paginación.
- Registro de usuarios (email obligatorio y único), login y logout.
- Perfil con biografía, sitio web y avatar; cambio de contraseña.
- Rutas protegidas: crear, editar, eliminar, "Mis posts" y perfil requieren login; editar/eliminar solo el autor (o staff).
- Páginas "Sobre mí" y "Contacto", y páginas de error 403/404 personalizadas.
- Panel de administración de Django configurado.
- Suite de tests automáticos (23 tests).

## Instalación

```bash
# 1. Clonar el repositorio
git clone <URL-DEL-REPOSITORIO>
cd blog_dante

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate          # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env              # En Windows: copy .env.example .env
# Editar .env y reemplazar SECRET_KEY por una clave propia. Para generar una:
# python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"

# 5. Crear la base de datos
python manage.py migrate

# 6. Iniciar el servidor
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

## Crear un superusuario

```bash
python manage.py createsuperuser
```

El panel de administración queda en <http://127.0.0.1:8000/admin/>.

## Datos de ejemplo (opcional)

Con al menos un superusuario creado:

```bash
python manage.py cargar_datos_demo
# o con un usuario específico:
python manage.py cargar_datos_demo --usuario mi_usuario
```

Crea 4 posts publicados y 1 borrador. Se puede ejecutar varias veces sin duplicar.

## Tests

```bash
python manage.py test
```

## Estructura

```
blog_project/   configuración del proyecto (settings, urls)
posts/          app del blog (modelos, vistas, formularios, plantillas, estáticos)
accounts/       app de usuarios (registro, login, perfil)
```

Las imágenes subidas se guardan en `media/` (no se versiona).

## Autor

**Dante Dirazar** — [LinkedIn](https://www.linkedin.com/in/dante-dirazar-6a0183274)

## Créditos

Plantilla [Clean Blog](https://github.com/StartBootstrap/startbootstrap-clean-blog) © Start Bootstrap, licencia MIT.
