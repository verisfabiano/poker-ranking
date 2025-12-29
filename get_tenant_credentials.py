#!/usr/bin/env python
"""
Script para recuperar credenciais de tenants no banco de dados.
Use para acessar o admin do Django no Railway.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tenant, TenantUser

print("=" * 80)
print("🔐 CREDENCIAIS DE TENANTS - ACESSO AO ADMIN DJANGO")
print("=" * 80)

# Listar todos os tenants
tenants = Tenant.objects.all()

if not tenants.exists():
    print("❌ Nenhum tenant encontrado!")
else:
    for tenant in tenants:
        print(f"\n📍 TENANT: {tenant.nome}")
        print(f"   ID: {tenant.id}")
        print(f"   Slug: {tenant.slug}")
        print(f"   Ativo: {'✓ Sim' if tenant.ativo else '✗ Não'}")
        print(f"   Email: {tenant.club_email or '—'}")
        print(f"   Telefone: {tenant.club_phone or '—'}")
        
        # Buscar admins do tenant
        tenant_admins = TenantUser.objects.filter(tenant=tenant, role='admin')
        
        if tenant_admins.exists():
            print(f"\n   👤 ADMINISTRADORES:")
            for tenant_user in tenant_admins:
                user = tenant_user.user
                print(f"      ├─ Username: {user.username}")
                print(f"      ├─ Email: {user.email}")
                print(f"      ├─ Role: {tenant_user.role}")
                print(f"      ├─ Superuser: {'✓ Sim' if user.is_superuser else '✗ Não'}")
                print(f"      └─ Staff: {'✓ Sim' if user.is_staff else '✗ Não'}")
        else:
            print(f"\n   ⚠️  Nenhum admin encontrado para este tenant!")

# Buscar superusers
print("\n" + "=" * 80)
print("🔑 SUPERUSERS (ACESSO TOTAL AO ADMIN):")
print("=" * 80)

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f"\n   ├─ Username: {user.username}")
        print(f"   ├─ Email: {user.email}")
        
        # Tenants do superuser
        user_tenants = TenantUser.objects.filter(user=user)
        if user_tenants.exists():
            print(f"   └─ Tenants: {', '.join([tu.tenant.nome for tu in user_tenants])}")
else:
    print("   Nenhum superuser encontrado!")

print("\n" + "=" * 80)
print("📖 COMO ACESSAR O ADMIN NO RAILWAY:")
print("=" * 80)
print("""
1. Vá para: https://seu-app.railway.app/admin/
   
2. Faça login com:
   - Username: (veja a saída acima)
   - Password: (a senha que você definiu ao criar)
   
3. Se esqueceu a senha:
   - Você pode resetar pelo Django shell:
   
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> user = User.objects.get(username='seu_username')
   >>> user.set_password('nova_senha')
   >>> user.save()
   
4. IMPORTANTE: 
   - Superusers têm acesso a TUDO
   - Admins de tenant têm acesso apenas ao seu tenant
   - Para mudar senhas no Railway, use: python manage.py changepassword username
""")

print("=" * 80)
