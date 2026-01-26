from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django import forms
from ..models import Tenant, TenantUser, Player
from ..decorators.rate_limit import rate_limit


class PlayerPublicRegistrationForm(forms.Form):
    """Formulário simplificado para registro público de jogadores"""
    nome = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo',
            'autofocus': True
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com'
        })
    )
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    password_confirm = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        email = cleaned_data.get('email')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'As senhas não conferem')

        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Este email já está registrado')

        return cleaned_data


@require_http_methods(["GET", "POST"])
@rate_limit(max_attempts=5, window_minutes=1)
def player_login_club(request, slug):
    """
    Login de jogador para um clube específico.
    URL: /clube/{slug}/login/
    """
    
    # Pegar o tenant pelo slug
    tenant = get_object_or_404(Tenant, slug=slug, ativo=True)
    
    # Se já está logado, redirecionar
    if request.user.is_authenticated:
        tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()
        if tenant_user:
            return redirect('player_home')
        return redirect('landing_page')
    
    error = None
    
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            error = 'Email e senha são obrigatórios'
        else:
            try:
                # Encontrar usuário por email
                user = User.objects.get(email=email)
                
                # Verificar se o usuário tem acesso a este tenant
                tenant_user = TenantUser.objects.filter(user=user, tenant=tenant).first()
                
                if not tenant_user:
                    error = 'Você não está registrado neste clube'
                else:
                    # Autenticar com o username
                    authenticated_user = authenticate(
                        request,
                        username=user.username,
                        password=password,
                        backend='django.contrib.auth.backends.ModelBackend'
                    )
                    
                    if authenticated_user:
                        login(request, authenticated_user)
                        return redirect('player_home')
                    else:
                        error = 'Email ou senha incorretos'
            except User.DoesNotExist:
                error = 'Email ou senha incorretos'
    
    context = {
        'tenant': tenant,
        'error': error,
    }
    return render(request, 'player_login_club.html', context)


@require_http_methods(["GET", "POST"])
def player_register_public(request, slug):
    """
    Registro público de jogador em um clube específico.
    URL: /clube/{slug}/registro/
    """
    
    # Pegar o tenant pelo slug
    tenant = get_object_or_404(Tenant, slug=slug, ativo=True)
    
    # Se já está logado como jogador deste tenant, redirecionar
    if request.user.is_authenticated:
        tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()
        if tenant_user:
            return redirect('player_home')
    
    if request.method == "POST":
        form = PlayerPublicRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                from ..services.email_service import EmailService
                
                with transaction.atomic():
                    # Dados do formulário
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    nome = form.cleaned_data['nome']
                    
                    # 1. Criar usuário (inativo até email ser verificado)
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=nome,
                        is_active=False  # Desativado até email ser verificado
                    )
                    
                    # 2. Vincular usuário ao tenant como jogador
                    TenantUser.objects.create(
                        user=user,
                        tenant=tenant,
                        role='player'
                    )
                    
                    # 3. Criar Player
                    Player.objects.create(
                        user=user,
                        tenant=tenant,
                        nome=nome,
                        apelido=nome,  # Usar nome como apelido por padrão
                        email=email,
                        ativo=True
                    )
                    
                    # 4. Enviar email de verificação
                    EmailService.send_verification_email(user, request)
                    
                    # Retornar para página de confirmação de email
                    return render(request, 'auth/email_verification_pending.html', {
                        'email': email,
                        'message': f'Um email de verificação foi enviado para {email}. Clique no link para ativar sua conta.'
                    })
                    
            except Exception as e:
                form.add_error(None, f'Erro ao registrar: {str(e)}')
        
        context = {
            'tenant': tenant,
            'form': form,
        }
        return render(request, 'player_register_public.html', context)
    
    # GET request
    form = PlayerPublicRegistrationForm()
    return render(request, 'player_register_public.html', {
        'tenant': tenant,
        'form': form
    })
