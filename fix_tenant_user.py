#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tenant, TenantUser
from django.contrib.auth.models import User as DjangoUser

# Get the correct tenant
tenant = Tenant.objects.get(slug='espacopoker')
user = DjangoUser.objects.get(username='espacopoker')

# Create or update tenant user
tenant_user, created = TenantUser.objects.get_or_create(
    user=user,
    tenant=tenant,
    defaults={'role': 'admin'}
)

if created:
    print(f"✅ Criado: {user.username} -> {tenant.nome} (admin)")
else:
    tenant_user.role = 'admin'
    tenant_user.save()
    print(f"✅ Atualizado: {user.username} -> {tenant.nome} (admin)")

print("\n=== TENANT USER AGORA ===")
for tu in TenantUser.objects.filter(user=user):
    print(f"  {tu.user.username} -> {tu.tenant.nome} (Role: {tu.role})")
