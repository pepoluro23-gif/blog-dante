from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactoForm, PostForm
from .models import Post

POSTS_POR_PAGINA = 5


def _puede_gestionar(user, post):
    """Solo el autor (o un usuario staff) puede editar o eliminar un post."""
    return user.is_authenticated and (post.autor_id == user.id or user.is_staff)


def lista_posts(request):
    """Listado público: solo posts publicados, con búsqueda y paginación."""
    busqueda = request.GET.get("q", "").strip()
    posts = Post.objects.filter(estado="publicado").select_related("autor")
    if busqueda:
        posts = posts.filter(
            Q(titulo__icontains=busqueda)
            | Q(subtitulo__icontains=busqueda)
            | Q(contenido__icontains=busqueda)
        )
    paginador = Paginator(posts, POSTS_POR_PAGINA)
    pagina = paginador.get_page(request.GET.get("page"))
    contexto = {"posts": pagina, "busqueda": busqueda}
    return render(request, "posts/lista_posts.html", contexto)


def detalle_post(request, slug):
    post = get_object_or_404(Post.objects.select_related("autor"), slug=slug)
    # Los borradores/archivados solo los ve su autor (o staff)
    if post.estado != "publicado" and not _puede_gestionar(request.user, post):
        raise PermissionDenied
    contexto = {"post": post, "puede_gestionar": _puede_gestionar(request.user, post)}
    return render(request, "posts/detalle_post.html", contexto)


@login_required
def mis_posts(request):
    """Posts del usuario logueado, incluidos borradores y archivados."""
    posts = Post.objects.filter(autor=request.user)
    return render(request, "posts/mis_posts.html", {"posts": posts})


@login_required
def crear_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, "El post se creó correctamente.")
            return redirect("detalle_post", slug=post.slug)
        messages.error(request, "Revisá los errores del formulario.")
    else:
        form = PostForm()
    contexto = {"form": form, "titulo_pagina": "Nuevo post", "texto_boton": "Publicar"}
    return render(request, "posts/post_form.html", contexto)


@login_required
def editar_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if not _puede_gestionar(request.user, post):
        raise PermissionDenied
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "El post se actualizó correctamente.")
            return redirect("detalle_post", slug=post.slug)
        messages.error(request, "Revisá los errores del formulario.")
    else:
        form = PostForm(instance=post)
    contexto = {
        "form": form,
        "post": post,
        "titulo_pagina": "Editar post",
        "texto_boton": "Guardar cambios",
    }
    return render(request, "posts/post_form.html", contexto)


@login_required
def eliminar_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if not _puede_gestionar(request.user, post):
        raise PermissionDenied
    # Nunca se borra por GET: GET muestra la confirmación, POST elimina.
    if request.method == "POST":
        post.delete()
        messages.success(request, "El post fue eliminado.")
        return redirect("lista_posts")
    return render(request, "posts/post_confirm_delete.html", {"post": post})


def acerca_de(request):
    return render(request, "posts/acerca_de.html")


def contacto(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            # En un proyecto real acá se enviaría un email o se guardaría el mensaje.
            nombre = form.cleaned_data["nombre"]
            messages.success(request, f"¡Gracias, {nombre}! Recibimos tu mensaje.")
            return redirect("contacto")
    else:
        form = ContactoForm()
    return render(request, "posts/contacto.html", {"form": form})
