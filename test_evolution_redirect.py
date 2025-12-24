#!/usr/bin/env python
"""
Teste para rastrear redirecionamentos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from core.models import Season, Player, Tenant

client = Client()
veris = Tenant.objects.get(slug='veris-poker')

# Acessar ranking (admin view)
print("\n=== TESTE 1: Acessar ranking ===")
response = client.get(f'/ranking/12/', follow=True)
print(f"Status: {response.status_code}")
print(f"URL final: {response.request['PATH_INFO']}")
content = response.content.decode('utf-8')

# Procurar a URL do botão evolução
import re
evolution_urls = re.findall(r'href="(/jogador/\d+/season/\d+/evolucao/)"', content)
print(f"URLs de evolução encontradas: {evolution_urls[:3]}")

print("\n=== TESTE 2: Acessar evolução diretamente ===")
response = client.get('/jogador/54/season/12/evolucao/')
print(f"Status: {response.status_code}")
print(f"URL final: {response.request['PATH_INFO']}")
if response.status_code == 200:
    print("✓ 200 OK")
else:
    print(f"✗ Status {response.status_code}")

print("\n=== TESTE 3: Simular clique no botão (new tab) ===")
response = client.get('/jogador/54/season/12/evolucao/', follow=True)
print(f"Status final: {response.status_code}")
print(f"URL final: {response.request['PATH_INFO']}")
print(f"Templates renderizados: {[t.name for t in response.templates]}")

# Procurar por "Temporada" ou "seasons_list" no conteúdo
content = response.content.decode('utf-8')
if 'Temporadas' in content:
    print("⚠ Conteúdo contém 'Temporadas' - pode estar na página errada")
elif 'Evolução' in content:
    print("✓ Conteúdo contém 'Evolução' - página correta")
