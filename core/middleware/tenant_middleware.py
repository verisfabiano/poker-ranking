from django.utils.deprecation import MiddlewareMixin
from ..managers.tenant_manager import set_current_tenant, get_current_tenant
from ..models import TenantUser
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que extrai o tenant do usuário autenticado
    e o coloca no contexto da thread.
    """
    
    def process_request(self, request):
        """
        Extrai tenant do usuário e define em request.tenant.
        """
        request.tenant = None
        
        if request.user.is_authenticated:
            try:
                # Pega o primeiro tenant do usuário (considere permitir seleção)
                tenant_user = TenantUser.objects.select_related('tenant').filter(
                    user=request.user
                ).first()
                
                if tenant_user and tenant_user.tenant.ativo:
                    request.tenant = tenant_user.tenant
                    set_current_tenant(request.tenant)
                    logger.info(f"Tenant set for user {request.user.username}: {request.tenant.nome}")
                else:
                    if tenant_user:
                        logger.warning(f"Tenant inactive for user {request.user.username}: {tenant_user.tenant.nome if tenant_user else 'None'}")
                    else:
                        logger.warning(f"No TenantUser found for user {request.user.username}")
            except Exception as e:
                logger.error(f"Error in TenantMiddleware: {str(e)}", exc_info=True)
        
        return None
    
    def process_response(self, request, response):
        """
        Limpa o tenant do contexto ao final do request.
        """
        set_current_tenant(None)
        return response
