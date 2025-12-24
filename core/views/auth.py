from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from ..models import Player

User = get_user_model()

# --- PERMISSÕES ---

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_player(user):
    return user.is_authenticated and not (user.is_staff or user.is_superuser)

admin_required = user_passes_test(is_admin, login_url="login")
player_required = user_passes_test(is_player, login_url="login")

@login_required
def home_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("painel_home")
    return redirect("player_home")

# --- AUTH JOGADOR ---

def player_login(request):
    mensagem = None
    if request.method == "POST":
        login_input = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()
        user = None

        if login_input:
            user_obj = User.objects.filter(email__iexact=login_input).first()
            if user_obj:
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=senha,
                    backend='django.contrib.auth.backends.ModelBackend'
                )
            else:
                user = authenticate(
                    request,
                    username=login_input,
                    password=senha,
                    backend='django.contrib.auth.backends.ModelBackend'
                )

        if user is not None:
            login(request, user)
            if is_admin(user):
                return HttpResponseRedirect(reverse("painel_home"))
            else:
                return HttpResponseRedirect(reverse("player_home"))
        else:
            mensagem = "E-mail ou senha inválidos."

    return render(request, "player_login.html", {"mensagem": mensagem})

def player_logout(request):
    logout(request)
    return redirect("player_login")