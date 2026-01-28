"""
Views de gerenciamento SUPERADMIN - para gerenciar todos os tenants
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.contrib.auth.models import User
from ..models import Tenant, TenantUser
from ..decorators.superadmin_decorators import superadmin_required


# ============================================================
#  DASHBOARD SUPERADMIN
# ============================================================

@superadmin_required
def superadmin_dashboard(request):
    """Dashboard do superadmin com estatísticas dos tenants"""
    
    tenants = Tenant.objects.annotate(
        total_users=Count('users', distinct=True)
    ).order_by('-criado_em')[:5]
    
    stats = {
        'total_tenants': Tenant.objects.count(),
        'tenants_ativos': Tenant.objects.filter(ativo=True).count(),
        'tenants_inativos': Tenant.objects.filter(ativo=False).count(),
        'total_usuarios': User.objects.count(),
        'total_superusers': User.objects.filter(is_superuser=True).count(),
    }
    
    return render(request, 'superadmin/dashboard.html', {
        'tenants': tenants,
        'stats': stats,
    })


# ============================================================
#  GERENCIAMENTO DE TENANTS
# ============================================================

@superadmin_required
def superadmin_tenants_list(request):
    """Lista todos os tenants com opções de edição e deleção"""
    
    # Filtros opcionais
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    tenants = Tenant.objects.annotate(
        total_users=Count('users', distinct=True)
    )
    
    if status:
        tenants = tenants.filter(ativo=(status == 'ativo'))
    
    if search:
        tenants = tenants.filter(nome__icontains=search) | tenants.filter(slug__icontains=search)
    
    tenants = tenants.order_by('-criado_em')
    
    return render(request, 'superadmin/tenants_list.html', {
        'tenants': tenants,
        'search': search,
        'status': status,
    })


@superadmin_required
def superadmin_tenant_create(request):
    """Criar novo tenant"""
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        slug = request.POST.get('slug', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        club_email = request.POST.get('club_email', '').strip()
        club_phone = request.POST.get('club_phone', '').strip()
        club_cnpj = request.POST.get('club_cnpj', '').strip()
        club_website = request.POST.get('club_website', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        # Validar
        errors = []
        if not nome:
            errors.append('Nome do tenant é obrigatório')
        if not slug:
            errors.append('Slug é obrigatório')
        if Tenant.objects.filter(slug=slug).exists():
            errors.append('Slug já existe')
        if not club_email:
            errors.append('Email do clube é obrigatório')
        
        if errors:
            return render(request, 'superadmin/tenant_form.html', {
                'errors': errors,
                'form_data': request.POST,
            })
        
        # Criar tenant
        tenant = Tenant.objects.create(
            nome=nome,
            slug=slug,
            descricao=descricao,
            club_email=club_email,
            club_phone=club_phone,
            club_cnpj=club_cnpj,
            club_website=club_website,
            ativo=ativo,
        )
        
        messages.success(request, f'Tenant "{nome}" criado com sucesso!')
        return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
    
    return render(request, 'superadmin/tenant_form.html', {
        'form_type': 'create',
    })


@superadmin_required
def superadmin_tenant_detail(request, tenant_id):
    """Detalhes do tenant com opções de edição e gerenciamento de admins"""
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    admins = TenantUser.objects.filter(tenant=tenant, role='admin').select_related('user')
    
    return render(request, 'superadmin/tenant_detail.html', {
        'tenant': tenant,
        'admins': admins,
    })


@superadmin_required
def superadmin_tenant_edit(request, tenant_id):
    """Editar informações do tenant"""
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        slug = request.POST.get('slug', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        club_email = request.POST.get('club_email', '').strip()
        club_phone = request.POST.get('club_phone', '').strip()
        club_cnpj = request.POST.get('club_cnpj', '').strip()
        club_website = request.POST.get('club_website', '').strip()
        ativo = request.POST.get('ativo') == 'on'
        
        # Validar
        errors = []
        if not nome:
            errors.append('Nome do tenant é obrigatório')
        if not slug:
            errors.append('Slug é obrigatório')
        if slug != tenant.slug and Tenant.objects.filter(slug=slug).exists():
            errors.append('Slug já existe')
        if not club_email:
            errors.append('Email do clube é obrigatório')
        
        if errors:
            return render(request, 'superadmin/tenant_form.html', {
                'form_type': 'edit',
                'tenant': tenant,
                'errors': errors,
                'form_data': request.POST,
            })
        
        # Atualizar tenant
        tenant.nome = nome
        tenant.slug = slug
        tenant.descricao = descricao
        tenant.club_email = club_email
        tenant.club_phone = club_phone
        tenant.club_cnpj = club_cnpj
        tenant.club_website = club_website
        tenant.ativo = ativo
        tenant.save()
        
        messages.success(request, f'Tenant "{nome}" atualizado com sucesso!')
        return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
    
    return render(request, 'superadmin/tenant_form.html', {
        'form_type': 'edit',
        'tenant': tenant,
    })


@superadmin_required
def superadmin_tenant_delete(request, tenant_id):
    """Deletar um tenant (com confirmação)"""
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao') == 'on'
        
        if not confirmacao:
            messages.error(request, 'Você deve confirmar a deleção')
            return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
        
        nome = tenant.nome
        
        # Deletar em transação para garantir integridade
        with transaction.atomic():
            # Deletar TenantUsers
            TenantUser.objects.filter(tenant=tenant).delete()
            # Deletar tenant (cascata deleta os modelos relacionados)
            tenant.delete()
        
        messages.success(request, f'Tenant "{nome}" deletado com sucesso!')
        return redirect('superadmin_tenants_list')
    
    # Mostrar confirmação
    return render(request, 'superadmin/tenant_delete_confirm.html', {
        'tenant': tenant,
    })


# ============================================================
#  GERENCIAMENTO DE ADMINS DO TENANT
# ============================================================

@superadmin_required
def superadmin_tenant_admin_add(request, tenant_id):
    """Adicionar admin a um tenant"""
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip()
        
        if not user_id:
            messages.error(request, 'Selecione um usuário')
            return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado')
            return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
        
        # Criar ou atualizar TenantUser
        tenant_user, created = TenantUser.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': 'admin'}
        )
        
        if not created:
            tenant_user.role = 'admin'
            tenant_user.save()
            messages.info(request, f'{user.username} já era admin do {tenant.nome}')
        else:
            messages.success(request, f'{user.username} adicionado como admin do {tenant.nome}')
        
        return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
    
    # Listar usuários que não são admins do tenant
    admins_ids = TenantUser.objects.filter(
        tenant=tenant, 
        role='admin'
    ).values_list('user_id', flat=True)
    
    usuarios = User.objects.exclude(id__in=admins_ids).order_by('username')
    
    return render(request, 'superadmin/tenant_admin_add.html', {
        'tenant': tenant,
        'usuarios': usuarios,
    })


@superadmin_required
def superadmin_tenant_admin_remove(request, tenant_id, user_id):
    """Remover admin de um tenant"""
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao') == 'on'
        
        if not confirmacao:
            messages.error(request, 'Você deve confirmar a remoção')
            return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
        
        TenantUser.objects.filter(user=user, tenant=tenant).delete()
        messages.success(request, f'{user.username} removido como admin do {tenant.nome}')
        return redirect('superadmin_tenant_detail', tenant_id=tenant.id)
    
    # Mostrar confirmação
    return render(request, 'superadmin/tenant_admin_remove_confirm.html', {
        'tenant': tenant,
        'user': user,
    })
