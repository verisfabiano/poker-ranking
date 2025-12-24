#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from core.models import Tenant, TenantUser

# Verificar tenant Veris
veris = Tenant.objects.filter(slug='veris').first()
if veris:
    print(f"Tenant: {veris.nome}")
    print(f"Slug: {veris.slug}")
    print(f"Ativo: {veris.ativo}")
    print(f"ID: {veris.id}")
    
    # Verificar admin do tenant
    admins = TenantUser.objects.filter(tenant=veris, role='admin')
    print(f"\nAdmins: {admins.count()}")
    for admin in admins:
        print(f"  - {admin.user.username} ({admin.user.email})")
else:
    print("Tenant 'veris' não encontrado")
    # Listar todos os tenants
    print("\nTenants disponíveis:")
    for t in Tenant.objects.all():
        print(f"  - {t.nome} (slug: {t.slug}, ativo: {t.ativo})")
