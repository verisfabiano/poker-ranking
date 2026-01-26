"""
Serviço de Email para Autenticação
Envia emails de verificação e reset de senha
"""
import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from django.contrib.auth.models import User


class EmailService:
    """Serviço centralizado para envio de emails de autenticação"""
    
    @staticmethod
    def send_verification_email(user, request=None):
        """
        Envia email de verificação para novo usuário
        
        Args:
            user: User model instance
            request: HTTP request (para construir URL absoluta)
        """
        from ..models import EmailVerificationToken
        
        # Criar token
        token = EmailVerificationToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # URL de verificação
        if request:
            site_url = f"{request.scheme}://{request.get_host()}"
        else:
            site_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        
        verify_url = f"{site_url}/auth/verify-email/{token.token}/"
        
        # Contexto para template
        context = {
            'user': user,
            'verify_url': verify_url,
            'expires_in_hours': 24,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'PokerClube'
        }
        
        # Renderizar template de email
        html_message = render_to_string('emails/verify_email.html', context)
        
        # Enviar
        try:
            send_mail(
                subject=f'Verifique seu email - {context["site_name"]}',
                message=f'Clique aqui para verificar: {verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True, "Email de verificação enviado"
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    @staticmethod
    def verify_email(token_string):
        """
        Verifica email usando token
        
        Args:
            token_string: Token de verificação
            
        Returns:
            (success, message, user)
        """
        from ..models import EmailVerificationToken
        
        try:
            token = EmailVerificationToken.objects.get(
                token=token_string,
                expires_at__gt=timezone.now(),
                verified_at__isnull=True
            )
        except EmailVerificationToken.DoesNotExist:
            return False, "Token inválido ou expirado", None
        
        # Ativar usuário
        user = token.user
        user.is_active = True
        user.save()
        
        # Marcar como verificado
        token.verified_at = timezone.now()
        token.save()
        
        return True, "Email verificado com sucesso!", user
    
    @staticmethod
    def send_password_reset_email(user, request=None):
        """
        Envia email de reset de senha
        
        Args:
            user: User model instance
            request: HTTP request
        """
        from ..models import PasswordResetToken
        
        # Deletar tokens antigos para este usuário
        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).delete()
        
        # Criar novo token
        token = PasswordResetToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=2)
        )
        
        # URL de reset
        if request:
            site_url = f"{request.scheme}://{request.get_host()}"
        else:
            site_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        
        reset_url = f"{site_url}/auth/reset-password/{token.token}/"
        
        # Contexto
        context = {
            'user': user,
            'reset_url': reset_url,
            'expires_in_hours': 2,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'PokerClube'
        }
        
        # Template
        html_message = render_to_string('emails/reset_password.html', context)
        
        # Enviar
        try:
            send_mail(
                subject=f'Redefinir Senha - {context["site_name"]}',
                message=f'Clique aqui para resetar: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True, "Email de reset enviado"
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    @staticmethod
    def reset_password(token_string, new_password):
        """
        Reset de senha com token
        
        Args:
            token_string: Token de reset
            new_password: Nova senha
            
        Returns:
            (success, message)
        """
        from ..models import PasswordResetToken
        
        try:
            token = PasswordResetToken.objects.get(
                token=token_string,
                expires_at__gt=timezone.now(),
                used_at__isnull=True
            )
        except PasswordResetToken.DoesNotExist:
            return False, "Link inválido ou expirado"
        
        # Validar senha
        if len(new_password) < 8:
            return False, "Senha deve ter no mínimo 8 caracteres"
        
        # Atualizar senha
        user = token.user
        user.set_password(new_password)
        user.save()
        
        # Marcar token como usado
        token.used_at = timezone.now()
        token.save()
        
        return True, "Senha alterada com sucesso!"
