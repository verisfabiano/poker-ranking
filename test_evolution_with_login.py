#!/usr/bin/env python
"""
Teste com login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
import re

client = Client()

# Fazer login
print("=== LOGIN ===")
login_success = client.login(username='testevris', password='testevris123')
print(f"Login: {'✓ Sucesso' if login_success else '✗ Falhou'}")

# Acessar ranking
print("\n=== TESTE 1: Acessar ranking ===")
response = client.get(f'/ranking/12/', follow=True)
print(f"Status: {response.status_code}")
print(f"URL final: {response.request['PATH_INFO']}")
content = response.content.decode('utf-8')

# Procurar a URL do botão evolução
evolution_urls = re.findall(r'href="(/jogador/\d+/season/\d+/evolucao/)"', content)
print(f"URLs de evolução encontradas: {evolution_urls[:5]}")

if evolution_urls:
    first_url = evolution_urls[0]
    print(f"\n=== TESTE 2: Acessar primeira URL encontrada: {first_url} ===")
    response = client.get(first_url)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.request['PATH_INFO']}")
    
    content = response.content.decode('utf-8')
    if 'Evolução' in content:
        print("✓ Página de evolução correta")
    elif 'Temporadas' in content:
        print("✗ Redirecionou para página de temporadas")
    else:
        print("? Página desconhecida")
