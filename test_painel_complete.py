#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 80)
print("TESTE COMPLETO: Login Veris e Acesso ao Painel")
print("=" * 80)

client = Client()

# Step 1: POST /jogador/login/
print("\n[STEP 1] POST /jogador/login/ com email='veris@veris.com' senha='veris123'")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

print(f"  Status: {response.status_code}")
print(f"  URL final: {response.request['PATH_INFO']}")

# Step 2: GET /painel/
print("\n[STEP 2] GET /painel/")
response = client.get('/painel/')

print(f"  Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8', errors='ignore')
    print(f"  Content-Length: {len(content)} bytes")
    
    # Verificar componentes principais
    checks = {
        '<!DOCTYPE html': 'HTML válido',
        '<html': 'Tag html',
        '<body': 'Tag body',
        'sidebar-admin': 'Sidebar',
        'painel_home.html': 'Template painel_home',
        'Painel de Controle': 'Título "Painel de Controle"',
        'Painel do Organizador': 'Título "Painel do Organizador"',
        'season-card': 'Cards de temporadas',
        'ranking-hero': 'Hero section',
        'page-header': 'Page header',
        'Temporadas': 'Section "Suas Temporadas"',
        'Acesso Rápido': 'Section "Acesso Rápido"',
        'btn btn-primary': 'Botões',
        '</html>': 'Fecha HTML',
    }
    
    print("\n  Verificacoes:")
    for check, desc in checks.items():
        if check in content:
            print(f"    [OK] {desc}")
        else:
            print(f"    [FALTA] {desc}")
    
    # Mostrar primeiros 1000 chars
    print(f"\n  Primeiros 1000 caracteres:")
    print("  " + "=" * 76)
    lines = content[:1000].split('\n')
    for line in lines[:30]:
        print(f"  {line}")
    print("  " + "=" * 76)
else:
    print(f"  [ERRO] Status inesperado: {response.status_code}")
    print(f"  Response: {response.content.decode('utf-8', errors='ignore')[:200]}")
