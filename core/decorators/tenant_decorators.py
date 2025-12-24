from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import redirect
from django.urls import reverse
from ..models import TenantUser


def tenant_role_required(*allowed_roles):
    """
    Decorator que valida se o usuário tem um dos roles permitidos no tenant.
    Deve ser usado APÓS @login_required.
    
    Uso:
        @login_required
        @tenant_role_required('admin', 'moderator')
        def minha_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Assume que @login_required já foi verificado
            
            if not hasattr(request, 'tenant') or not request.tenant:
                return JsonResponse({'error': 'Tenant não definido'}, status=403)
            
            try:
                tenant_user = TenantUser.objects.get(
                    user=request.user,
                    tenant=request.tenant
                )
                
                if tenant_user.role not in allowed_roles:
                    return JsonResponse(
                        {'error': f'Role "{tenant_user.role}" não tem permissão'},
                        status=403
                    )
            except TenantUser.DoesNotExist:
                return JsonResponse({'error': 'Sem acesso a este tenant'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Atalho para exigir login + tenant + role 'admin'.
    Combina @login_required com validação de TenantUser.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Primeiro checka login
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        
        # Depois checa tenant + role
        if not hasattr(request, 'tenant') or not request.tenant:
            return JsonResponse({'error': 'Tenant não definido'}, status=403)
        
        try:
            tenant_user = TenantUser.objects.get(
                user=request.user,
                tenant=request.tenant
            )
            
            if tenant_user.role != 'admin':
                return JsonResponse(
                    {'error': f'Acesso negado. Você é {tenant_user.role}.'},
                    status=403
                )
        except TenantUser.DoesNotExist:
            return JsonResponse({'error': 'Sem acesso a este tenant'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def moderator_or_admin_required(view_func):
    """Atalho para exigir role 'admin' ou 'moderator'."""
    return tenant_role_required('admin', 'moderator')(view_func)

