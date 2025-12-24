#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de login e acesso ao painel para veris@veris.com
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("=" * 70)
print("TESTE: Login e Acesso ao Painel")
print("=" * 70)

# Verificar se usuário existe
try:
    user = User.objects.get(username='veris')
    print(f"\n[OK] Usuario encontrado: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   is_staff: {user.is_staff}")
except User.DoesNotExist:
    print(f"\n[ERRO] Usuario 'veris' nao encontrado")
    sys.exit(1)

# Verificar TenantUser
from core.models import TenantUser
tenant_users = TenantUser.objects.filter(user=user)
print(f"\n[OK] TenantUsers encontrados: {tenant_users.count()}")
for tu in tenant_users:
    print(f"   - {tu.tenant.nome} (role: {tu.role}, ativo: {tu.tenant.ativo})")

# Teste de Login e Acesso ao Painel
print("\n" + "=" * 70)
print("Simulando requisicao HTTP")
print("=" * 70)

client = Client()

# POST /jogador/login/
print("\n1. POST /jogador/login/ com username='veris' password='veris123'")
response = client.post('/jogador/login/', {
    'username': 'veris',
    'password': 'veris123'
}, follow=False)

print(f"   Status: {response.status_code}")
if response.status_code == 302:
    print(f"   [OK] Redirecionado para: {response['Location']}")
else:
    print(f"   [ERRO] Status inesperado")

# GET /painel/
print("\n2. GET /painel/")
response = client.get('/painel/')

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8', errors='ignore')
    print(f"   Content-Type: {response.get('Content-Type')}")
    print(f"   Tamanho: {len(content)} bytes")
    
    # Verificar conteúdo esperado
    if 'Painel de Controle' in content:
        print(f"   [OK] Pagina renderizou corretamente!")
    elif 'Painel do Organizador' in content:
        print(f"   [OK] Pagina renderizou corretamente (encontrou titulo)!")
    else:
        print(f"   [AVISO] Pagina renderizou mas nao tem conteudo esperado")
        print(f"   Primeiros 300 chars: {content[:300]}")
        
    # Verificar sidebar
    if 'sidebar-admin' in content:
        print(f"   [OK] Sidebar encontrada")
    else:
        print(f"   [AVISO] Sidebar nao encontrada")
else:
    print(f"   [ERRO] Status inesperado")
    content = response.content.decode('utf-8', errors='ignore')
    print(f"   Response: {content[:200]}")

print("\n" + "=" * 70)
print("FIM DO TESTE")
print("=" * 70)
