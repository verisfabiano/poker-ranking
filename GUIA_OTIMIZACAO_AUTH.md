# 🔧 Guia de Otimização - Fluxo de Autenticação

**Data:** Jan 26, 2026  
**Referência:** ANALISE_AUTH_FLUXO.md

---

## 1. 🎯 Implementação Rápida (Ordem Recomendada)

### Etapa 1: Rate Limiting (30 min) 🚀

**Instalar dependência:**
```bash
pip install django-ratelimit
```

**Criar arquivo:** `core/decorators/rate_limit.py`
```python
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

def login_ratelimit(view_func):
    """Limita 5 tentativas por minuto por IP"""
    return ratelimit(
        key='ip',
        rate='5/m',
        method='POST',
        message='Muitas tentativas de login. Tente novamente em 1 minuto.'
    )(view_func)
```

**Aplicar em views:**
```python
# core/views/auth.py
from core.decorators.rate_limit import login_ratelimit

@login_ratelimit
def player_login(request):
    ...

# core/views/public.py
@login_ratelimit
def login_view(request):
    ...

# core/views/player_public.py
@login_ratelimit
def player_login_club(request, slug):
    ...
```

**Adicionar em settings.py:**
```python
# django-ratelimit
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

**Resultado:** Login protegido contra brute force ✅

---

### Etapa 2: Validação de Email (1h)

**Criar arquivo:** `core/services/email_service.py`
```python
import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from core.models import EmailVerificationToken

class EmailService:
    
    @staticmethod
    def send_verification_email(user, request=None):
        """Envia email de verificação"""
        token = EmailVerificationToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # URL de verificação
        verify_url = f"{settings.SITE_URL}/auth/verify-email/{token.token}/"
        
        # Template do email
        context = {
            'user': user,
            'verify_url': verify_url,
            'expires_in_hours': 24
        }
        
        html_message = render_to_string('emails/verify_email.html', context)
        
        send_mail(
            subject=f'Verifique seu email - {settings.SITE_NAME}',
            message=f'Clique aqui para verificar: {verify_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    @staticmethod
    def verify_email(token_string):
        """Verifica email usando token"""
        token = EmailVerificationToken.objects.filter(
            token=token_string,
            expires_at__gt=timezone.now(),
            verified_at__isnull=True
        ).first()
        
        if not token:
            return False, "Token inválido ou expirado"
        
        # Marcar como verificado
        user = token.user
        user.is_active = True
        user.save()
        
        token.verified_at = timezone.now()
        token.save()
        
        return True, "Email verificado com sucesso!"
```

**Criar modelo:** `core/models.py` (adicionar)
```python
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        return self.verified_at is None and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"Verificação de {self.user.email}"
```

**Atualizar signup:**
```python
# core/views/player_public.py
def player_register_public(request, slug):
    ...
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=False  # ← Começa inativo!
    )
    
    # Envia email de verificação
    EmailService.send_verification_email(user)
    
    return render(request, 'auth/verify_email_pending.html', {
        'email': email
    })
```

**Criar view de verificação:**
```python
# core/views/auth.py
def verify_email(request, token):
    success, message = EmailService.verify_email(token)
    
    if success:
        return render(request, 'auth/email_verified.html', {
            'message': message,
            'success': True
        })
    else:
        return render(request, 'auth/email_verified.html', {
            'message': message,
            'success': False
        })
```

**Adicionar URL:**
```python
# core/urls.py
path('auth/verify-email/<str:token>/', verify_email, name='verify_email'),
```

**Resultado:** Emails validados, contas seguras ✅

---

### Etapa 3: Recuperação de Senha (1.5h)

**Criar arquivo:** `core/services/password_reset_service.py`
```python
import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from core.models import PasswordResetToken

class PasswordResetService:
    
    @staticmethod
    def request_reset(email):
        """Cria token de reset e envia email"""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Não revelar se email existe (segurança)
            return True, "Se o email existir, receberá instrções"
        
        # Deletar tokens antigos
        PasswordResetToken.objects.filter(user=user).delete()
        
        # Criar novo token
        token = PasswordResetToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=2)
        )
        
        # URL de reset
        reset_url = f"{settings.SITE_URL}/auth/reset-password/{token.token}/"
        
        # Enviar email
        context = {
            'user': user,
            'reset_url': reset_url,
            'expires_in_hours': 2
        }
        
        html_message = render_to_string('emails/reset_password.html', context)
        
        send_mail(
            subject=f'Resetar Senha - {settings.SITE_NAME}',
            message=f'Clique aqui: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True, "Se o email existir, receberá instruções"
    
    @staticmethod
    def reset_password(token_string, new_password):
        """Reset password com token"""
        token = PasswordResetToken.objects.filter(
            token=token_string,
            expires_at__gt=timezone.now(),
            used_at__isnull=True
        ).first()
        
        if not token:
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
```

**Criar modelo:**
```python
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()
    
    def __str__(self):
        return f"Reset de {self.user.email}"
```

**Criar views:**
```python
# core/views/auth.py
from core.services.password_reset_service import PasswordResetService

def forgot_password(request):
    """Tela para solicitar reset"""
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        success, message = PasswordResetService.request_reset(email)
        
        return render(request, 'auth/reset_password_sent.html', {
            'email': email,
            'message': message
        })
    
    return render(request, 'auth/forgot_password.html')

def reset_password(request, token):
    """Reset de senha com token"""
    # Validar que token existe
    try:
        reset_token = PasswordResetToken.objects.get(
            token=token,
            expires_at__gt=timezone.now(),
            used_at__isnull=True
        )
    except PasswordResetToken.DoesNotExist:
        return render(request, 'auth/reset_password_invalid.html')
    
    if request.method == "POST":
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        if not password or password != password_confirm:
            return render(request, 'auth/reset_password_form.html', {
                'token': token,
                'error': 'Senhas não conferem ou estão vazias'
            })
        
        success, message = PasswordResetService.reset_password(token, password)
        
        if success:
            return render(request, 'auth/reset_password_success.html')
        else:
            return render(request, 'auth/reset_password_form.html', {
                'token': token,
                'error': message
            })
    
    return render(request, 'auth/reset_password_form.html', {'token': token})
```

**Adicionar URLs:**
```python
# core/urls.py
path('auth/forgot-password/', forgot_password, name='forgot_password'),
path('auth/reset-password/<str:token>/', reset_password, name='reset_password'),
```

**Resultado:** Usuários podem resetar senha sem contatar suporte ✅

---

## 2. 📋 Estrutura Unificada de Rotas

**Proposta nova para `core/urls.py`:**

```python
# ===== AUTENTICAÇÃO =====
# Rotas genéricas de auth
urlpatterns += [
    # Login/Logout genérico
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    
    # Cadastro
    path('auth/register/', player_register, name='register'),
    path('auth/register/club/', signup_club, name='register_club'),
    
    # Email
    path('auth/verify-email/<str:token>/', verify_email, name='verify_email'),
    
    # Senha
    path('auth/forgot-password/', forgot_password, name='forgot_password'),
    path('auth/reset-password/<str:token>/', reset_password, name='reset_password'),
]

# Rotas específicas por clube
urlpatterns += [
    path('club/<slug:slug>/auth/login/', player_login_club, name='club_login'),
    path('club/<slug:slug>/auth/register/', player_register_club, name='club_register'),
    path('club/<slug:slug>/auth/logout/', logout_view, name='club_logout'),
]
```

**Antes (confuso):**
```
/login
/jogador/login
/registro
/clube/{slug}/login
/clube/{slug}/registro
/cadastro-clube
```

**Depois (claro):**
```
/auth/login
/auth/register
/auth/register/club
/club/{slug}/auth/login
/club/{slug}/auth/register
```

---

## 3. 🎨 Templates Unificados

**Criar pasta:** `core/templates/auth/`

**Base template:** `base_auth.html`
```html
{% extends 'base.html' %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <div class="auth-header">
            {% if title %}
                <h2>{{ title }}</h2>
            {% endif %}
            {% if subtitle %}
                <p class="text-muted">{{ subtitle }}</p>
            {% endif %}
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
        
        {% if form_errors %}
            <div class="alert alert-danger">
                {{ form_errors }}
            </div>
        {% endif %}
        
        <div class="auth-body">
            {% block auth_content %}{% endblock %}
        </div>
        
        <div class="auth-footer">
            {% block auth_footer %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}
```

**CSS:** `static/css/auth.css`
```css
.auth-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
}

.auth-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    width: 100%;
    max-width: 400px;
    padding: 40px;
}

.auth-header {
    text-align: center;
    margin-bottom: 30px;
}

.auth-header h2 {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
}

.auth-header p {
    font-size: 14px;
    color: #666;
}

.auth-body {
    margin-bottom: 20px;
}

.auth-footer {
    border-top: 1px solid #eee;
    padding-top: 20px;
    text-align: center;
    font-size: 14px;
}

.auth-footer a {
    color: #667eea;
    text-decoration: none;
    font-weight: bold;
}

@media (max-width: 576px) {
    .auth-card {
        padding: 20px;
    }
    
    .auth-header h2 {
        font-size: 22px;
    }
}
```

---

## 4. 📧 Templates de Email

**Arquivo:** `core/templates/emails/verify_email.html`
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .button { 
            background: #667eea; 
            color: white; 
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 4px; 
            display: inline-block; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Bem-vindo ao PokerClube!</h2>
        <p>Oi {{ user.get_full_name|default:user.username }},</p>
        
        <p>Clique no botão abaixo para verificar seu email e ativar sua conta:</p>
        
        <p>
            <a href="{{ verify_url }}" class="button">Verificar Email</a>
        </p>
        
        <p>Este link expira em {{ expires_in_hours }} horas.</p>
        
        <p>Se não solicitou este email, ignore esta mensagem.</p>
        
        <hr>
        <p style="font-size: 12px; color: #999;">
            © PokerClube 2026
        </p>
    </div>
</body>
</html>
```

**Arquivo:** `core/templates/emails/reset_password.html`
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .button { 
            background: #667eea; 
            color: white; 
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 4px; 
            display: inline-block; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Redefinir Senha</h2>
        <p>Oi {{ user.get_full_name|default:user.username }},</p>
        
        <p>Clique no botão abaixo para redefinir sua senha:</p>
        
        <p>
            <a href="{{ reset_url }}" class="button">Redefinir Senha</a>
        </p>
        
        <p>Este link expira em {{ expires_in_hours }} horas.</p>
        
        <p><strong>Aviso de Segurança:</strong> Se não solicitou o reset de senha, ignore este email e sua conta permanecerá segura.</p>
        
        <hr>
        <p style="font-size: 12px; color: #999;">
            © PokerClube 2026
        </p>
    </div>
</body>
</html>
```

---

## 5. 🧪 Testes para Autenticação

**Arquivo:** `core/tests/test_auth.py`
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import EmailVerificationToken, PasswordResetToken

class AuthenticationTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_login_success(self):
        """Teste login bem-sucedido"""
        response = self.client.post('/auth/login/', {
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_login_invalid_email(self):
        """Teste login com email inválido"""
        response = self.client.post('/auth/login/', {
            'email': 'wrong@example.com',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 200)  # Volta para form
        self.assertContains(response, 'Email ou senha inválidos')
    
    def test_rate_limiting(self):
        """Teste rate limiting no login"""
        for i in range(6):
            self.client.post('/auth/login/', {
                'email': 'test@example.com',
                'password': 'WrongPass'
            })
        
        # 6ª tentativa deve ser bloqueada
        response = self.client.post('/auth/login/', {
            'email': 'test@example.com',
            'password': 'TestPass123'
        })
        self.assertContains(response, 'Muitas tentativas')
    
    def test_register_creates_inactive_user(self):
        """Teste que registro cria usuário inativo"""
        response = self.client.post('/auth/register/', {
            'nome': 'Novo Jogador',
            'apelido': 'NJ',
            'email': 'novo@example.com',
            'senha': 'NewPass123'
        })
        
        user = User.objects.get(email='novo@example.com')
        self.assertFalse(user.is_active)  # Deve ser inativo
    
    def test_email_verification(self):
        """Teste verificação de email"""
        token = EmailVerificationToken.objects.create(
            user=self.user,
            token='test-token-123',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        response = self.client.get(f'/auth/verify-email/{token.token}/')
        self.assertEqual(response.status_code, 200)
        
        # Usuário deve estar ativo agora
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.is_active)
    
    def test_password_reset(self):
        """Teste reset de senha"""
        response = self.client.post('/auth/forgot-password/', {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        
        # Deve ter criado token
        self.assertTrue(
            PasswordResetToken.objects.filter(user=self.user).exists()
        )
```

**Rodar testes:**
```bash
python manage.py test core.tests.test_auth -v 2
```

---

## 6. 📝 Migração de Dados

Se há usuários existentes, precisa migrar:

```python
# Arquivo: core/migrations/0033_migrate_active_status.py
from django.db import migrations
from django.contrib.auth.models import User

def mark_existing_users_active(apps, schema_editor):
    """Marca usuários existentes como ativos"""
    User.objects.filter(is_active=False).update(is_active=True)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0032_...'),
    ]

    operations = [
        migrations.RunPython(mark_existing_users_active),
    ]
```

---

## 7. ✅ Checklist de Implementação

- [ ] Instalar `django-ratelimit`
- [ ] Criar `core/decorators/rate_limit.py`
- [ ] Aplicar rate limiting em login
- [ ] Criar `EmailVerificationToken` model
- [ ] Criar `core/services/email_service.py`
- [ ] Criar view `verify_email`
- [ ] Criar template email de verificação
- [ ] Atualizar signup para criar usuário inativo
- [ ] Criar `PasswordResetToken` model
- [ ] Criar `core/services/password_reset_service.py`
- [ ] Criar views de forgot/reset password
- [ ] Criar templates de email de reset
- [ ] Reorganizar URLs em `core/urls.py`
- [ ] Criar pasta `core/templates/auth/`
- [ ] Criar templates unificados
- [ ] Criar `core/static/css/auth.css`
- [ ] Criar testes em `core/tests/test_auth.py`
- [ ] Rodar testes
- [ ] Documentar mudanças
- [ ] Fazer PR para revisão

---

## 8. 🚀 Estimativa de Tempo

| Tarefa | Tempo |
|--------|-------|
| Rate Limiting | 30 min |
| Email Validation | 1h |
| Password Reset | 1.5h |
| Reorganizar URLs | 1h |
| Templates Unificados | 1.5h |
| Testes | 1h |
| Documentação | 30 min |
| **Total** | **7 horas** |

Pode ser feito em 2-3 dias de desenvolvimento!

