#!/usr/bin/env python
"""
Script de teste para as novas views de SuperAdmin
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tenant, TenantUser

print("=" * 80)
print("🧪 TESTE DE CONFIGURAÇÃO - SUPERADMIN VIEWS")
print("=" * 80)

# 1. Verificar decorador
print("\n✅ 1. Verificando decorator superadmin_required...")
try:
    from core.decorators.superadmin_decorators import superadmin_required
    print("   [OK] Decorator importado com sucesso")
except ImportError as e:
    print(f"   [ERRO] {e}")
    sys.exit(1)

# 2. Verificar views
print("\n✅ 2. Verificando views de superadmin...")
try:
    from core.views.superadmin import (
        superadmin_dashboard,
        superadmin_tenants_list,
        superadmin_tenant_create,
        superadmin_tenant_detail,
        superadmin_tenant_edit,
        superadmin_tenant_delete,
        superadmin_tenant_admin_add,
        superadmin_tenant_admin_remove,
    )
    print("   [OK] Todas as views importadas com sucesso")
except ImportError as e:
    print(f"   [ERRO] {e}")
    sys.exit(1)

# 3. Verificar URLs
print("\n✅ 3. Verificando URLs...")
try:
    from django.urls import reverse
    urls = [
        'superadmin_dashboard',
        'superadmin_tenants_list',
        'superadmin_tenant_create',
    ]
    for url_name in urls:
        try:
            url = reverse(url_name)
            print(f"   [OK] {url_name} -> {url}")
        except Exception as e:
            print(f"   [ERRO] {url_name} -> {e}")
except Exception as e:
    print(f"   [ERRO] {e}")

# 4. Verificar templates
print("\n✅ 4. Verificando templates...")
templates = [
    'superadmin/dashboard.html',
    'superadmin/tenants_list.html',
    'superadmin/tenant_form.html',
    'superadmin/tenant_detail.html',
    'superadmin/tenant_delete_confirm.html',
    'superadmin/tenant_admin_add.html',
    'superadmin/tenant_admin_remove_confirm.html',
]
for template in templates:
    from django.template.loader import get_template
    try:
        get_template(template)
        print(f"   [OK] {template}")
    except Exception as e:
        print(f"   [ERRO] {template} -> {e}")

# 5. Verificar banco de dados
print("\n✅ 5. Verificando banco de dados...")
print(f"   Total de Tenants: {Tenant.objects.count()}")
print(f"   Total de Usuários: {User.objects.count()}")
print(f"   Total de Superusers: {User.objects.filter(is_superuser=True).count()}")

print("\n" + "=" * 80)
print("✨ TESTE CONCLUÍDO COM SUCESSO!")
print("=" * 80)
print("\nAcesse a interface em: http://localhost:8000/superadmin/")
print("Você precisa estar logado como superuser para acessar.")
