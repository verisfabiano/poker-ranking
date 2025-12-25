from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from ..models import Tenant, TenantUser, Player
from ..validators import ValidadorCNPJ, ValidadorCEP, ValidadorCPF, ValidadorTelefone, ValidadorEndereço


def landing_page(request):
    """Landing page inicial - sem autenticação necessária"""
    if request.user.is_authenticated:
        # Se já está logado, redireciona para painel
        return redirect('painel_home')
    
    # Buscar todos os clubes ativos
    clubs = Tenant.objects.filter(ativo=True).order_by('nome')
    
    return render(request, 'landing_page.html', {'clubs': clubs})


@require_http_methods(["GET", "POST"])
def signup_club(request):
    """Cadastro de novo clube (tenant) + usuário administrador"""
    
    if request.user.is_authenticated:
        return redirect('painel_home')
    
    if request.method == "POST":
        # ===== DADOS DO CLUBE =====
        club_name = request.POST.get('club_name', '').strip()
        club_description = request.POST.get('club_description', '').strip()
        club_email = request.POST.get('club_email', '').strip()
        club_phone = request.POST.get('club_phone', '').strip()
        club_cnpj = request.POST.get('club_cnpj', '').strip()
        club_website = request.POST.get('club_website', '').strip()
        
        # ===== ENDEREÇO DO CLUBE =====
        address_cep = request.POST.get('address_cep', '').strip()
        address_street = request.POST.get('address_street', '').strip()
        address_number = request.POST.get('address_number', '').strip()
        address_complement = request.POST.get('address_complement', '').strip()
        address_neighborhood = request.POST.get('address_neighborhood', '').strip()
        address_city = request.POST.get('address_city', '').strip()
        address_state = request.POST.get('address_state', '').strip()
        
        # ===== DADOS DO ADMINISTRADOR =====
        admin_full_name = request.POST.get('admin_full_name', '').strip()
        admin_phone = request.POST.get('admin_phone', '').strip()
        admin_cpf = request.POST.get('admin_cpf', '').strip()
        admin_role = request.POST.get('admin_role', '').strip()
        
        # ===== DADOS DA CONTA =====
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        errors = {}
        
        # ===== VALIDAÇÕES - CLUBE =====
        if not club_name:
            errors['club_name'] = 'Nome do clube é obrigatório'
        
        if not club_email:
            errors['club_email'] = 'Email de contato é obrigatório'
        
        if club_cnpj:
            try:
                ValidadorCNPJ.validar(club_cnpj)
            except Exception as e:
                errors['club_cnpj'] = str(e)
        
        if club_phone:
            try:
                ValidadorTelefone.validar(club_phone)
            except Exception as e:
                errors['club_phone'] = str(e)
        
        # ===== VALIDAÇÕES - ENDEREÇO =====
        if address_cep:
            try:
                ValidadorCEP.validar(address_cep)
            except Exception as e:
                errors['address_cep'] = str(e)
        
        if address_state:
            try:
                ValidadorEndereço.validar_uf(address_state)
            except Exception as e:
                errors['address_state'] = str(e)
        
        # ===== VALIDAÇÕES - ADMINISTRADOR =====
        if not admin_full_name:
            errors['admin_full_name'] = 'Nome completo do administrador é obrigatório'
        
        if not admin_phone:
            errors['admin_phone'] = 'Telefone do administrador é obrigatório'
        else:
            try:
                ValidadorTelefone.validar(admin_phone)
            except Exception as e:
                errors['admin_phone'] = str(e)
        
        if admin_cpf:
            try:
                ValidadorCPF.validar(admin_cpf)
            except Exception as e:
                errors['admin_cpf'] = str(e)
        
        # ===== VALIDAÇÕES - CONTA =====
        if not email:
            errors['email'] = 'Email é obrigatório'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Este email já está registrado'
        
        if not password:
            errors['password'] = 'Senha é obrigatória'
        elif len(password) < 8:
            errors['password'] = 'Senha deve ter pelo menos 8 caracteres'
        
        if password != password_confirm:
            errors['password_confirm'] = 'As senhas não conferem'
        
        if not errors:
            try:
                with transaction.atomic():
                    # 1. Criar Tenant (clube)
                    slug = slugify(club_name)
                    # Garantir slug único
                    base_slug = slug
                    counter = 1
                    while Tenant.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Formatar dados antes de salvar
                    if club_cnpj:
                        club_cnpj = ValidadorCNPJ.formatar(club_cnpj)
                    else:
                        club_cnpj = None  # Salvar como NULL, não como string vazia
                    
                    if club_phone:
                        club_phone = ValidadorTelefone.formatar(club_phone)
                    if address_cep:
                        address_cep = ValidadorCEP.formatar(address_cep)
                    if admin_phone:
                        admin_phone = ValidadorTelefone.formatar(admin_phone)
                    if admin_cpf:
                        admin_cpf = ValidadorCPF.formatar(admin_cpf)
                    
                    tenant = Tenant.objects.create(
                        nome=club_name,
                        slug=slug,
                        descricao=club_description,
                        club_email=club_email,
                        club_phone=club_phone,
                        club_cnpj=club_cnpj,
                        club_website=club_website,
                        address_cep=address_cep,
                        address_street=address_street,
                        address_number=address_number,
                        address_complement=address_complement,
                        address_neighborhood=address_neighborhood,
                        address_city=address_city,
                        address_state=address_state,
                        admin_full_name=admin_full_name,
                        admin_phone=admin_phone,
                        admin_cpf=admin_cpf,
                        admin_role=admin_role,
                        ativo=True
                    )
                    
                    # 2. Criar usuário
                    username = email.split('@')[0]
                    # Garantir username único
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=admin_full_name.split()[0] if admin_full_name else '',
                        last_name=' '.join(admin_full_name.split()[1:]) if admin_full_name and len(admin_full_name.split()) > 1 else ''
                    )
                    
                    # 3. Vincular usuário ao tenant como admin
                    TenantUser.objects.create(
                        user=user,
                        tenant=tenant,
                        role='admin'
                    )
                    
                    # 4. Criar Player para o usuário (admin do clube)
                    Player.objects.get_or_create(
                        user=user,
                        tenant=tenant,
                        defaults={
                            'nome': admin_full_name or email.split('@')[0].capitalize(),
                            'apelido': email.split('@')[0],
                            'email': email,
                        }
                    )
                    
                    # 5. Fazer login automático
                    user = authenticate(
                        request,
                        username=username,
                        password=password,
                        backend='django.contrib.auth.backends.ModelBackend'
                    )
                    if user:
                        login(request, user)
                    
                    return redirect('painel_home')
                    
            except Exception as e:
                errors['general'] = f'Erro ao criar clube: {str(e)}'
        
        context = {
            'errors': errors,
            'club_name': club_name,
            'club_description': club_description,
            'club_email': club_email,
            'club_phone': club_phone,
            'club_cnpj': club_cnpj,
            'club_website': club_website,
            'address_cep': address_cep,
            'address_street': address_street,
            'address_number': address_number,
            'address_complement': address_complement,
            'address_neighborhood': address_neighborhood,
            'address_city': address_city,
            'address_state': address_state,
            'admin_full_name': admin_full_name,
            'admin_phone': admin_phone,
            'admin_cpf': admin_cpf,
            'admin_role': admin_role,
            'email': email,
        }
        return render(request, 'signup_club.html', context)
    
    return render(request, 'signup_club.html')


def login_view(request):
    """Página de login"""
    if request.user.is_authenticated:
        return redirect('painel_home')
    
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(
                request,
                username=user.username,
                password=password,
                backend='django.contrib.auth.backends.ModelBackend'
            )
            
            if user is not None:
                login(request, user)
                return redirect('painel_home')
            else:
                error = 'Email ou senha incorretos'
        except User.DoesNotExist:
            error = 'Email ou senha incorretos'
        
        return render(request, 'login.html', {
            'error': error,
            'email': email,
        })
    
    return render(request, 'login.html')
