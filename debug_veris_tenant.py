#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import TenantUser, Tenant, Season

print("=" * 60)
print("DEBUG: USUÁRIO VERIS")
print("=" * 60)

try:
    user = User.objects.get(username='veris')
    print(f"\n✓ Usuário encontrado:")
    print(f"  ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Staff: {user.is_staff}")
    
    print(f"\n✓ TenantUsers do veris:")
    tenant_users = TenantUser.objects.filter(user=user)
    if tenant_users.exists():
        for tu in tenant_users:
            print(f"  - Tenant: {tu.tenant.nome}")
            print(f"    Tenant ID: {tu.tenant.id}")
            print(f"    Tenant Ativo: {tu.tenant.ativo}")
            print(f"    Role: {tu.role}")
            
            # Verificar seasons do tenant
            seasons = Season.objects.filter(tenant=tu.tenant)
            print(f"    Seasons: {seasons.count()}")
            for season in seasons:
                print(f"      - {season.nome} (Ativa: {season.ativo})")
    else:
        print("  ❌ NENHUM TenantUser encontrado!")
        print("\n  ⚠️ ESSE É O PROBLEMA! O usuário 'veris' não está associado a nenhum tenant!")
    
except User.DoesNotExist:
    print("❌ Usuário 'veris' não encontrado!")
