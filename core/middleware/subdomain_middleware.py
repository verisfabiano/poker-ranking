from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class SubdomainTenantMiddleware(MiddlewareMixin):
    """
    Extrai tenant do subdomínio.
    Ex: tenant1.example.com → tenant com slug 'tenant1'
    """
    
    def process_request(self, request):
        host = request.get_host().lower()
        
        # Remove porta se existir
        if ':' in host:
            host = host.split(':')[0]
        
        parts = host.split('.')
        
        # Se tiver subdomínio (www.example.com ou tenant.example.com)
        if len(parts) >= 3:
            subdomain = parts[0]
            
            # Ignora 'www'
            if subdomain != 'www':
                try:
                    request.tenant = Tenant.objects.get(slug=subdomain, ativo=True)
                except Tenant.DoesNotExist:
                    request.tenant = None
        
        return None
