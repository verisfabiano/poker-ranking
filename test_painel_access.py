#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from core.models import TenantUser
from core.views.season import painel_home

# Teste 1: Simular request através do client
print("=" * 60)
print("TESTE 1: Login e acesso a /painel/")
print("=" * 60)

client = Client()

# Login
response = client.post('/login/', {'username': 'veris', 'password': 'veris123'})
print(f"POST /login/ -> Status: {response.status_code}")
print(f"Redirect: {response.url if hasattr(response, 'url') else 'N/A'}")

# Acessar painel
response = client.get('/painel/')
print(f"\nGET /painel/ -> Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
print(f"Content Length: {len(response.content)} bytes")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'Painel de Controle' in content:
        print("✅ Página renderizou corretamente (encontrou 'Painel de Controle')")
    else:
        print("❌ Página está em branco ou sem conteúdo esperado")
        # Mostrar primeiros 500 chars
        print(f"Content preview: {content[:500]}")
elif response.status_code == 403:
    print("❌ ERRO 403: Acesso negado")
    print(f"Response: {response.content.decode('utf-8')[:200]}")
else:
    print(f"❌ Status inesperado: {response.status_code}")
