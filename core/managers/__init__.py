from django.db import models
from threading import local

_thread_locals = local()


def get_current_tenant():
    """Retorna o tenant do contexto atual."""
    return getattr(_thread_locals, 'tenant', None)


def set_current_tenant(tenant):
    """Define o tenant no contexto atual."""
    _thread_locals.tenant = tenant


class TenantQuerySet(models.QuerySet):
    """
    QuerySet que auto-filtra por tenant se disponível.
    """
    def for_tenant(self, tenant):
        """Filtra explicitamente por tenant."""
        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    """
    Manager que fornece queries filtradas automaticamente por tenant.
    """
    
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant:
            qs = qs.filter(tenant=tenant)
        return qs
    
    def for_tenant(self, tenant):
        """Query explícita para um tenant específico."""
        return super().get_queryset().filter(tenant=tenant)
    
    def all_tenants(self):
        """Retorna queryset sem filtro de tenant."""
        return super().get_queryset()
