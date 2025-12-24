# Este arquivo é apenas para organizar imports de modelos multi-tenant
# Os modelos principais ainda estão em core.models.py

from .tenant import Tenant, TenantUser

__all__ = ['Tenant', 'TenantUser']

# Certifique-se que seus modelos têm:
# - ForeignKey(Tenant) com related_name
# - objects = TenantManager()
# - class Meta: constraints para garantir unicidade com tenant

__all__ = ['Tenant', 'TenantUser', 'Season', 'Player', 'Tournament', ...]
