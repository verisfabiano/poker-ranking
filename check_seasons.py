#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Setup django antes de importar qualquer modelo
django.setup()

from django.contrib.auth.models import User
from core.models import Season, TenantUser

# Buscar o usuário veris
user = User.objects.get(username='veris')
tenant_user = TenantUser.objects.filter(user=user).first()

if tenant_user:
    tenant = tenant_user.tenant
    print(f"Tenant: {tenant.nome}")
    print(f"Tenant Ativo: {tenant.ativo}")
    
    # Buscar seasons  do tenant
    seasons = Season.objects.filter(tenant=tenant).order_by("-data_inicio")
    print(f"\nTotal de Seasons: {seasons.count()}")
    
    if seasons.exists():
        print("\nSeasons encontradas:")
        for season in seasons:
            print(f"  - {season.nome} (ID: {season.id}, Ativa: {season.ativo})")
    else:
        print("\n❌ NENHUMA SEASON ENCONTRADA PARA ESTE TENANT!")
else:
    print("❌ Usuário veris não tem TenantUser associado!")
