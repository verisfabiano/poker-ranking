from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from ..models import Player # Note o ..models (volta uma pasta)

User = get_user_model()

# --- PERMISSÕES ---

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

admin_required = user_passes_test(is_admin, login_url="player_login")

@login_required
def home_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("painel_home") # Ajustado para nome da URL
    return redirect("player_tournaments")

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
                user = authenticate(request, username=user_obj.username, password=senha)
            else:
                user = authenticate(request, username=login_input, password=senha)

        if user is not None:
            login(request, user)
            if is_admin(user):
                return HttpResponseRedirect(reverse("painel_home"))
            else:
                return HttpResponseRedirect(reverse("player_tournaments"))
        else:
            mensagem = "E-mail ou senha inválidos."

    return render(request, "player_login.html", {"mensagem": mensagem})

def player_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("player_login"))

def player_register(request):
    mensagem = None
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        apelido = request.POST.get("apelido", "").strip()
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "").strip()

        if not (nome and email and senha):
            mensagem = "Preencha nome, e-mail e senha."
        elif User.objects.filter(username=email).exists():
            mensagem = "Este e-mail já está cadastrado."
        else:
            user = User.objects.create_user(username=email, email=email, password=senha)
            Player.objects.create(user=user, nome=nome, apelido=apelido or None, ativo=True)
            login(request, user)
            return HttpResponseRedirect(reverse("player_tournaments"))

    return render(request, "player_register.html", {"mensagem": mensagem})