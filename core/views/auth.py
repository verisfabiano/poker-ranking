from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from ..models import Player, EmailVerificationToken, PasswordResetToken
from ..decorators.rate_limit import rate_limit
from ..services.email_service import EmailService

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

@rate_limit(max_attempts=5, window_minutes=1)
def player_login(request):
    mensagem = None
    email_para_verificar = None
    
    if request.method == "POST":
        login_input = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()
        user = None

        if login_input:
            user_obj = User.objects.filter(email__iexact=login_input).first()
            if user_obj:
                # Verificar se email não foi verificado
                if not user_obj.is_active:
                    email_para_verificar = user_obj.email
                    mensagem = "⚠️ Sua conta precisa ser ativada. Verifique seu email para continuar."
                    return render(request, "player_login.html", {
                        "mensagem": mensagem,
                        "email_para_verificar": email_para_verificar,
                        "email": login_input
                    })
                
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

        if user is not None and user.is_active:
            login(request, user)
            
            # Registrar login bem-sucedido
            from ..models import TenantAuditLog
            if hasattr(request, 'tenant') and request.tenant:
                TenantAuditLog.log_action(
                    request,
                    request.tenant,
                    'LOGIN',
                    success=True,
                    description=f"Login bem-sucedido para {user.email}"
                )
            
            if is_admin(user):
                return HttpResponseRedirect(reverse("painel_home"))
            else:
                return HttpResponseRedirect(reverse("player_home"))
        elif user is not None and not user.is_active:
            mensagem = "⚠️ Sua conta não foi ativada. Verifique seu email."
            return render(request, "player_login.html", {
                "mensagem": mensagem,
                "email_para_verificar": user.email,
                "email": login_input
            })
        else:
            mensagem = "E-mail ou senha inválidos."
            
            # Registrar tentativa de login falhada
            from ..models import TenantAuditLog
            if hasattr(request, 'tenant') and request.tenant:
                TenantAuditLog.log_action(
                    request,
                    request.tenant,
                    'LOGIN_FAILED',
                    success=False,
                    description=f"Tentativa de login falhada com email: {login_input}"
                )

    return render(request, "player_login.html", {"mensagem": mensagem})

def player_logout(request):
    logout(request)
    return redirect("player_login")


# ============================================================
#  EMAIL VERIFICATION & PASSWORD RESET
# ============================================================

@require_http_methods(["GET"])
def verify_email(request, token):
    """
    Verifica o email do usuário usando um token.
    GET /auth/verify-email/<token>/
    """
    try:
        email_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return render(request, "auth/verify_email_error.html", {
            "error": "Token inválido ou expirado.",
            "error_code": "invalid_token"
        }, status=400)
    
    # Verificar se o token já foi usado
    if email_token.verified_at:
        return render(request, "auth/verify_email_error.html", {
            "error": "Este email já foi verificado anteriormente.",
            "error_code": "already_verified"
        })
    
    # Verificar se expirou
    if email_token.is_expired():
        return render(request, "auth/verify_email_error.html", {
            "error": "O token expirou. Por favor, solicite um novo link de verificação.",
            "error_code": "token_expired"
        }, status=400)
    
    # Marcar como verificado
    with transaction.atomic():
        if email_token.verify():
            return render(request, "auth/verify_email_success.html", {
                "user": email_token.user,
                "message": "Seu email foi verificado com sucesso! Você já pode fazer login."
            })
    
    # Erro inesperado
    return render(request, "auth/verify_email_error.html", {
        "error": "Erro ao verificar email. Tente novamente mais tarde.",
        "error_code": "verification_failed"
    }, status=500)


@require_http_methods(["GET", "POST"])
@rate_limit(max_attempts=5, window_minutes=1, key_prefix="forgot_password")
def forgot_password(request):
    """
    Página para solicitar reset de senha.
    GET: Exibe formulário
    POST: Envia email com link de reset
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        
        if not email:
            return render(request, "auth/forgot_password.html", {
                "error": "Por favor, informe seu email."
            })
        
        try:
            user = User.objects.get(email__iexact=email)
            
            # Invalidar tokens anteriores
            PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
                used_at=timezone.now()
            )
            
            # Enviar email com novo token
            EmailService.send_password_reset_email(user, request)
            
            # Mostrar mensagem de sucesso (sem revelar se email existe ou não - segurança)
            return render(request, "auth/forgot_password_success.html", {
                "email": email,
                "message": "Se este email está registrado em nossa sistema, você receberá um link para redefinir sua senha."
            })
        
        except User.DoesNotExist:
            # Não revelar se email existe ou não (melhor prática de segurança)
            return render(request, "auth/forgot_password_success.html", {
                "email": email,
                "message": "Se este email está registrado em nossa sistema, você receberá um link para redefinir sua senha."
            })
        
        except Exception as e:
            return render(request, "auth/forgot_password.html", {
                "error": f"Erro ao enviar email: {str(e)}",
                "email": email
            })
    
    return render(request, "auth/forgot_password.html")


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    """
    Página para redefinir a senha usando um token.
    GET: Exibe formulário
    POST: Processa a nova senha
    """
    try:
        password_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, "auth/reset_password_error.html", {
            "error": "Token inválido ou expirado.",
            "error_code": "invalid_token"
        }, status=400)
    
    # Verificar se o token já foi usado
    if password_token.used_at:
        return render(request, "auth/reset_password_error.html", {
            "error": "Este link de reset já foi utilizado. Solicite um novo link.",
            "error_code": "token_already_used"
        })
    
    # Verificar se expirou
    if password_token.is_expired():
        return render(request, "auth/reset_password_error.html", {
            "error": "O token expirou. Por favor, solicite um novo link de reset.",
            "error_code": "token_expired"
        }, status=400)
    
    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        password_confirm = request.POST.get("password_confirm", "").strip()
        
        # Validações
        if not password or not password_confirm:
            return render(request, "auth/reset_password.html", {
                "token": token,
                "error": "Ambos os campos de senha são obrigatórios."
            })
        
        if password != password_confirm:
            return render(request, "auth/reset_password.html", {
                "token": token,
                "error": "As senhas não correspondem."
            })
        
        if len(password) < 8:
            return render(request, "auth/reset_password.html", {
                "token": token,
                "error": "A senha deve ter no mínimo 8 caracteres."
            })
        
        try:
            # Redefinir senha e marcar token como usado
            with transaction.atomic():
                user = password_token.user
                user.set_password(password)
                user.save()
                password_token.mark_as_used()
            
            return render(request, "auth/reset_password_success.html", {
                "message": "Sua senha foi redefinida com sucesso! Você já pode fazer login."
            })
        
        except Exception as e:
            return render(request, "auth/reset_password.html", {
                "token": token,
                "error": f"Erro ao redefinir senha: {str(e)}"
            })
    
    return render(request, "auth/reset_password.html", {
        "token": token,
        "user_email": password_token.user.email
    })


# ============================================================
#  RESEND VERIFICATION EMAIL
# ============================================================

@require_http_methods(["POST"])
@rate_limit(max_attempts=3, window_minutes=5, key_prefix="resend_verification")
def resend_verification_email(request):
    """
    Re-envia o email de verificação para um email não confirmado.
    POST /auth/resend-verification-email/
    """
    email = request.POST.get("email", "").strip()
    
    if not email:
        return render(request, "auth/resend_verification.html", {
            "error": "Por favor, informe seu email."
        })
    
    try:
        user = User.objects.get(email__iexact=email)
        
        if user.is_active:
            # Email já foi verificado
            return render(request, "auth/resend_verification_success.html", {
                "email": email,
                "message": "Este email já foi verificado. Você já pode fazer login!"
            })
        
        # Invalidar tokens anteriores
        EmailVerificationToken.objects.filter(user=user, verified_at__isnull=True).update(
            expires_at=timezone.now()
        )
        
        # Enviar novo token
        EmailService.send_verification_email(user, request)
        
        return render(request, "auth/resend_verification_success.html", {
            "email": email,
            "message": f"Um novo link de verificação foi enviado para {email}. Verifique sua caixa de entrada."
        })
    
    except User.DoesNotExist:
        # Não revelar se email existe ou não (segurança)
        return render(request, "auth/resend_verification_success.html", {
            "email": email,
            "message": f"Se este email estiver registrado em nosso sistema, você receberá um link de verificação."
        })