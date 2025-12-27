"""
Views de gerenciamento SUPERADMIN - para gerenciar todos os clientes
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from ..models import Tenant, TenantUser


def is_superadmin(user):
    """Verifica se o usuário é superadmin (is_staff + is_superuser)"""
    return user.is_staff and user.is_superuser


superadmin_required = user_passes_test(is_superadmin, login_url="login")


@superadmin_required
def clientes_list(request):
    """
    Lista todos os clientes/clubes cadastrados no sistema.
    Apenas superadmin pode acessar.
    """
    # Buscar parâmetros de filtro/busca
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')  # 'ativo' ou 'inativo'
    
    # Query base
    clientes = Tenant.objects.all().order_by('-criado_em')
    
    # Filtros
    if search:
        clientes = clientes.filter(
            Q(nome__icontains=search) | 
            Q(slug__icontains=search) |
            Q(cnpj__icontains=search) |
            Q(telefone__icontains=search)
        )
    
    if status == 'ativo':
        clientes = clientes.filter(status=True)
    elif status == 'inativo':
        clientes = clientes.filter(status=False)
    
    # Adicionar contagem de usuários para cada cliente
    cliente_data = []
    for cliente in clientes:
        usuarios = TenantUser.objects.filter(tenant=cliente).count()
        cliente_data.append({
            'tenant': cliente,
            'total_usuarios': usuarios
        })
    
    context = {
        'cliente_data': cliente_data,
        'search': search,
        'status': status,
        'total_clientes': Tenant.objects.count(),
    }
    
    return render(request, 'superadmin/clientes_list.html', context)


@superadmin_required
def cliente_detail(request, cliente_id):
    """
    Detalhes de um cliente específico.
    """
    cliente = get_object_or_404(Tenant, id=cliente_id)
    usuarios = TenantUser.objects.filter(tenant=cliente).select_related('user')
    
    # Construir URL de registro dinâmica baseada no domínio atual
    registration_url = request.build_absolute_uri(f'/clube/{cliente.slug}/registro/')
    
    context = {
        'cliente': cliente,
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
        'registration_url': registration_url,
    }
    
    return render(request, 'superadmin/cliente_detail.html', context)


@superadmin_required
@require_http_methods(["POST"])
def cliente_slug_update(request, cliente_id):
    """
    Atualiza o slug de um cliente via AJAX.
    """
    cliente = get_object_or_404(Tenant, id=cliente_id)
    novo_slug = request.POST.get('slug', '').strip().lower()
    
    if not novo_slug:
        return JsonResponse({
            'success': False,
            'error': 'Slug não pode estar vazio'
        }, status=400)
    
    # Validar se slug é único (excluindo o cliente atual)
    if Tenant.objects.filter(slug=novo_slug).exclude(id=cliente_id).exists():
        return JsonResponse({
            'success': False,
            'error': f'Slug "{novo_slug}" já está em uso'
        }, status=400)
    
    # Validar formato: apenas letras, números e hífen
    if not all(c.isalnum() or c == '-' for c in novo_slug):
        return JsonResponse({
            'success': False,
            'error': 'Slug pode conter apenas letras, números e hífens'
        }, status=400)
    
    # Atualizar
    cliente.slug = novo_slug
    cliente.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Slug atualizado para "{novo_slug}"',
        'novo_slug': novo_slug
    })


@superadmin_required
@require_http_methods(["POST"])
def cliente_toggle_status(request, cliente_id):
    """
    Ativa/desativa um cliente.
    """
    cliente = get_object_or_404(Tenant, id=cliente_id)
    novo_status = request.POST.get('status', '').lower() == 'true'
    
    cliente.status = novo_status
    cliente.save()
    
    status_label = 'ativo' if novo_status else 'inativo'
    return JsonResponse({
        'success': True,
        'message': f'Cliente marcado como {status_label}',
        'novo_status': novo_status
    })
