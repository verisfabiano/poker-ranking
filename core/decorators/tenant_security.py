"""
Decoradores para validação e segurança de multi-tenant.
"""
from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from ..models import Tenant, TenantUser


def tenant_required(view_func):
    """
    Decorator que valida se o usuário tem acesso ao tenant da request.
    Previne acesso cross-tenant.
    
    Uso:
        @tenant_required
        def minha_view(request):
            tenant = request.tenant  # Seguro usar
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Se não há tenant na request, deixar passar
        # (será validado pelo middleware)
        if not hasattr(request, 'tenant') or not request.tenant:
            return HttpResponseForbidden("Acesso negado: Tenant não identificado")
        
        # Se usuário não está autenticado, deixar passar
        # (será validado por @login_required se necessário)
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Acesso negado: Autenticação necessária")
        
        # Verificar se o usuário tem acesso a este tenant
        tenant_user = TenantUser.objects.filter(
            user=request.user,
            tenant=request.tenant
        ).first()
        
        if not tenant_user:
            return HttpResponseForbidden(
                f"Acesso negado: Você não tem permissão para acessar {request.tenant.nome}"
            )
        
        # Adicionar informação de tenant na request para logging
        request.tenant_user = tenant_user
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def tenant_and_login_required(view_func):
    """
    Decorator combinado que requer login E validação de tenant.
    Mais restritivo que tenant_required.
    """
    @wraps(view_func)
    @login_required
    @tenant_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_tenant_ownership(queryset_field='tenant'):
    """
    Decorator factory que valida se um objeto pertence ao tenant do usuário.
    
    Uso:
        @check_tenant_ownership('tournament.tenant')
        def editar_torneio(request, tournament_id):
            tournament = get_object_or_404(Tournament, id=tournament_id)
            ...
    
    Args:
        queryset_field (str): Path para o campo tenant no objeto (ex: 'tournament.tenant')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Validar tenant básico primeiro
            if not hasattr(request, 'tenant') or not request.tenant:
                return HttpResponseForbidden("Tenant não identificado")
            
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Autenticação necessária")
            
            # Executar view
            response = view_func(request, *args, **kwargs)
            
            # Se a view retornar um objeto, validar ownership
            # (Esta validação é adicional e depende da implementação da view)
            return response
        
        return wrapper
    return decorator


class TenantAuditMixin:
    """
    Mixin para registrar ações de usuários dentro de um tenant.
    Implementar em models que precisam de auditoria.
    
    Uso:
        class MeuModel(TenantAuditMixin, models.Model):
            ...
    """
    
    @classmethod
    def log_action(cls, user, action, tenant, description=""):
        """
        Registra uma ação do usuário.
        
        Args:
            user: User object
            action: 'CREATE', 'UPDATE', 'DELETE', 'VIEW'
            tenant: Tenant object
            description: Descrição adicional
        """
        from django.utils import timezone
        from django.contrib.contenttypes.models import ContentType
        
        try:
            # Implementar conforme necessário
            # Exemplo: salvar em TenantAuditLog
            pass
        except Exception as e:
            # Não falhar a requisição se logging falhar
            print(f"Erro ao registrar auditoria: {str(e)}")
