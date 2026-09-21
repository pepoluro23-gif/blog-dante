from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PerfilForm, RegistroUsuarioForm
from .models import Perfil


def registro(request):
    if request.user.is_authenticated:
        return redirect("lista_posts")
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # El Perfil se crea automáticamente con una señal (accounts/signals.py)
            form.save()
            messages.success(request, "Cuenta creada. Ya podés iniciar sesión.")
            return redirect("login")
    else:
        form = RegistroUsuarioForm()
    return render(request, "accounts/registro.html", {"form": form})


@login_required
def perfil(request):
    perfil_usuario, _ = Perfil.objects.get_or_create(user=request.user)
    posts = request.user.posts.filter(estado="publicado")
    contexto = {"perfil": perfil_usuario, "posts": posts}
    return render(request, "accounts/perfil.html", contexto)


@login_required
def editar_perfil(request):
    # Siempre se edita el perfil del usuario logueado (nunca por ID en la URL)
    perfil_usuario, _ = Perfil.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil_usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil fue actualizado.")
            return redirect("perfil")
        messages.error(request, "Revisá los errores del formulario.")
    else:
        form = PerfilForm(instance=perfil_usuario)
    return render(request, "accounts/editar_perfil.html", {"form": form})
