from django.urls import path

from . import views

# Las rutas específicas van antes que la genérica <slug:slug>/
urlpatterns = [
    path("", views.lista_posts, name="lista_posts"),
    path("sobre-mi/", views.acerca_de, name="acerca_de"),
    path("contacto/", views.contacto, name="contacto"),
    path("mis-posts/", views.mis_posts, name="mis_posts"),
    path("posts/crear/", views.crear_post, name="crear_post"),
    path("posts/<slug:slug>/editar/", views.editar_post, name="editar_post"),
    path("posts/<slug:slug>/eliminar/", views.eliminar_post, name="eliminar_post"),
    path("posts/<slug:slug>/", views.detalle_post, name="detalle_post"),
]
