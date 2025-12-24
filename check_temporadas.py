#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("="*80)
print("TESTE: O que renderiza em /temporadas/")
print("="*80)

client = Client()

# Login
print("\n[1] Fazendo login...")
client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# Acessar /temporadas/
print("[2] GET /temporadas/")
response = client.get('/temporadas/')

html = response.content.decode('utf-8', errors='ignore')
print(f"    Status: {response.status_code}")
print(f"    Tamanho: {len(html)} bytes")

# Procurar <main>
if '<main' in html:
    print("    [OK] <main> encontrada")
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if main_match:
        main_content = main_match.group(1)
        print(f"    Tamanho do <main>: {len(main_content)} bytes")
        print(f"    Primeiros 300 chars:")
        print(f"    {main_content[:300]}")
else:
    print("    [ERRO] <main> NÃO encontrada!")

# Procurar elementos
elements = {
    'Season': html.count('season'),
    'Table': html.count('<table'),
    'Temporada': html.count('Temporada'),
    'Data': html.count('data_inicio'),
}

print("\n[3] Elementos encontrados:")
for elem, count in elements.items():
    print(f"    {elem}: {count}")

# Salvar para análise
with open('c:\\projetos\\poker_ranking\\temporadas_check.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n[4] HTML salvo em: c:\\projetos\\poker_ranking\\temporadas_check.html")
