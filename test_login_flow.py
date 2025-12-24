#!/usr/bin/env python
"""
Script para testar o fluxo de login e redirecionamento
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import TenantUser

# Criar cliente Django
client = Client()

print("=" * 70)
print("TESTE DE FLUXO DE LOGIN")
print("=" * 70)

# ====================================================================
# TESTE 1: Login com Admin de Tenant (veris)
# ====================================================================
print("\n[TESTE 1] Login com ADMIN de Tenant (veris@veris.com)")
print("-" * 70)

response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'  # Ajuste a senha conforme necessário
}, follow=False)

print(f"Status Code: {response.status_code}")
print(f"URL Redirecionada: {response.url if response.status_code in [301, 302, 303, 307, 308] else 'Nenhum redirecionamento'}")

if response.status_code in [301, 302, 303, 307, 308]:
    if '/painel/' in response.url:
        print("✅ SUCESSO: Admin foi redirecionado para /painel/")
    else:
        print(f"❌ ERRO: Admin foi redirecionado para {response.url} ao invés de /painel/")
else:
    if response.status_code == 200:
        print("❌ ERRO: Login falhou (página de login redisplayed)")
        if 'inválidos' in response.content.decode():
            print("   Mensagem de erro: E-mail ou senha inválidos")
    else:
        print(f"❌ ERRO: Status code inesperado: {response.status_code}")

# ====================================================================
# TESTE 2: Login com Jogador Comum
# ====================================================================
print("\n[TESTE 2] Login com JOGADOR Comum")
print("-" * 70)

# Buscar um jogador comum
player_user = User.objects.filter(is_staff=False).exclude(username='testevris').first()

if player_user:
    print(f"Testando com usuário: {player_user.username} ({player_user.email})")
    
    response = client.post('/jogador/login/', {
        'email': player_user.email,
        'senha': 'test123'  # Senha padrão para teste
    }, follow=False)
    
    print(f"Status Code: {response.status_code}")
    print(f"URL Redirecionada: {response.url if response.status_code in [301, 302, 303, 307, 308] else 'Nenhum redirecionamento'}")
    
    if response.status_code in [301, 302, 303, 307, 308]:
        if '/jogador/' in response.url or 'player_home' in response.url:
            print("✅ SUCESSO: Jogador foi redirecionado para /jogador/home/")
        else:
            print(f"❌ ERRO: Jogador foi redirecionado para {response.url} ao invés de /jogador/home/")
    else:
        print("❌ ERRO: Login falhou")
else:
    print("⚠️  Nenhum jogador comum encontrado para teste")

# ====================================================================
# TESTE 3: Verificar dados do usuário veris
# ====================================================================
print("\n[TESTE 3] Verificação de Dados - Usuário Veris")
print("-" * 70)

try:
    veris_user = User.objects.get(username='veris')
    print(f"Username: {veris_user.username}")
    print(f"Email: {veris_user.email}")
    print(f"is_staff: {veris_user.is_staff}")
    print(f"is_superuser: {veris_user.is_superuser}")
    
    # Verificar TenantUser
    tenant_users = TenantUser.objects.filter(user=veris_user)
    print(f"\nTenantUsers: {tenant_users.count()}")
    for tu in tenant_users:
        print(f"  - Tenant: {tu.tenant.nome}")
        print(f"    Role: {tu.role}")
        print(f"    Tenant Ativo: {tu.tenant.ativo}")
    
    # Determinar redirecionamento esperado
    if veris_user.is_staff or veris_user.is_superuser:
        print(f"\n✅ Deve ser redirecionado para: /painel/")
    else:
        print(f"\n✅ Deve ser redirecionado para: /jogador/home/")
        
except User.DoesNotExist:
    print("❌ Usuário 'veris' não encontrado")

# ====================================================================
# TESTE 4: Tentar acessar /painel/ sem login
# ====================================================================
print("\n[TESTE 4] Acessar /painel/ SEM Login")
print("-" * 70)

# Criar novo cliente sem sessão
client_no_session = Client()

response = client_no_session.get('/painel/', follow=False)
print(f"Status Code: {response.status_code}")
print(f"URL: {response.url if response.status_code in [301, 302, 303, 307, 308] else response.wsgi_request.path}")

if response.status_code in [301, 302]:
    if '/jogador/login/' in response.url:
        print("✅ SUCESSO: Redirecionado para /jogador/login/ (esperado)")
    else:
        print(f"❌ ERRO: Redirecionado para {response.url} ao invés de /jogador/login/")
else:
    print(f"❌ ERRO: Status code {response.status_code} (esperado 302)")

# ====================================================================
# TESTE 5: Verificar senha do usuário veris
# ====================================================================
print("\n[TESTE 5] Testes de Senha - Usuário Veris")
print("-" * 70)

veris_user = User.objects.get(username='veris')

# Listar possíveis senhas para teste
print("Tentando possíveis senhas...")
senhas_teste = [
    'veris123',
    'veris',
    'test123',
    '123456',
    'Veris123',
]

from django.contrib.auth import authenticate

for senha in senhas_teste:
    user = authenticate(username='veris', password=senha)
    if user:
        print(f"✅ Senha correta encontrada: '{senha}'")
        break
else:
    print("❌ Nenhuma das senhas testadas funcionou")
    print("   Use: python manage.py changepassword veris")

print("\n" + "=" * 70)
print("FIM DOS TESTES")
print("=" * 70)
