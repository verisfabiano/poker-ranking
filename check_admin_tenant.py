#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tenant, TenantUser

# Listar todos os usuários
print("=" * 50)
print("TODOS OS USUÁRIOS:")
print("=" * 50)
for user in User.objects.all():
    print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Superuser: {user.is_superuser} | Staff: {user.is_staff}")

print("\n" + "=" * 50)
print("TENANTS:")
print("=" * 50)
for tenant in Tenant.objects.all():
    print(f"ID: {tenant.id} | Nome: {tenant.nome}")

print("\n" + "=" * 50)
print("VERIS POKER - INFORMAÇÕES:")
print("=" * 50)
try:
    veris = Tenant.objects.get(nome__icontains="veris")
    print(f"\nTenant: {veris.nome}")
    print(f"ID: {veris.id}")
    
    # Buscar admins do tenant
    admins = TenantUser.objects.filter(tenant=veris, role='admin')
    print(f"\nAdministradores:")
    for admin in admins:
        user = admin.user
        print(f"  - Username: {user.username}")
        print(f"    Email: {user.email}")
        print(f"    Role: {admin.role}")
        print(f"    Superuser: {user.is_superuser}")
        print()
except Tenant.DoesNotExist:
    print("Tenant 'Veris' não encontrado!")
except Exception as e:
    print(f"Erro: {e}")
