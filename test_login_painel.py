#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 70)
print("TESTE: Login e Acesso ao Painel (com follow=True)")
print("=" * 70)

client = Client()

# POST /jogador/login com follow=True
print("\n1. POST /jogador/login/ com email='veris@veris.com' senha='veris123'")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

print(f"   Status final: {response.status_code}")
print(f"   URL final: {response.request['PATH_INFO']}")
print(f"   Redirect chain: {response.redirect_chain if hasattr(response, 'redirect_chain') else 'N/A'}")

# GET /painel/
print("\n2. GET /painel/")
response = client.get('/painel/')

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8', errors='ignore')
    print(f"   Content-Type: {response.get('Content-Type')}")
    print(f"   Tamanho: {len(content)} bytes")
    
    # Verificar conteudo esperado
    if 'Painel de Controle' in content:
        print(f"   [OK] Pagina renderizou corretamente!")
    elif 'Painel do Organizador' in content:
        print(f"   [OK] Pagina renderizou corretamente (encontrou titulo)!")
    elif 'sidebar-admin' in content:
        print(f"   [OK] Sidebar encontrada")
    else:
        print(f"   [AVISO] Pagina renderizou mas conteudo pode estar vazio")
        print(f"   Primeiros 500 chars:")
        print(f"   {content[:500]}")
else:
    print(f"   [ERRO] Status inesperado: {response.status_code}")
