#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("="*80)
print("TESTE: Verificar <main> tag no HTML renderizado")
print("="*80)

client = Client()

# 1. Login
print("\n[1] Fazendo login...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# 2. Acessar /painel/
print("[2] GET /painel/")
response = client.get('/painel/')
html = response.content.decode('utf-8', errors='ignore')

print(f"    Status: {response.status_code}")
print(f"    Tamanho total: {len(html)} bytes")

# 3. Procurar <main>
if '<main' in html:
    print("\n[OK] <main> tag ENCONTRADA no HTML")
    
    # Extrair conteúdo do main
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if main_match:
        main_content = main_match.group(1)
        print(f"    Tamanho do conteúdo: {len(main_content)} bytes")
        print(f"    Primeiros 200 chars:")
        print(f"    {main_content[:200]}")
    else:
        print("    [ALERTA] <main> encontrada mas conteúdo não extraído")
else:
    print("\n[ERRO] <main> tag NÃO encontrada!")

# 4. Procurar <body>
if '<body' in html:
    print("\n[OK] <body> tag encontrada")
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if body_match:
        body_content = body_match.group(1)
        print(f"    Tamanho do conteúdo: {len(body_content)} bytes")
        
        # Contar elementos principais
        sidebar_count = body_content.count('sidebar-admin')
        navbar_count = body_content.count('<nav')
        main_count = body_content.count('<main')
        
        print(f"    sidebar-admin: {sidebar_count}")
        print(f"    <nav>: {navbar_count}")
        print(f"    <main>: {main_count}")
else:
    print("\n[ERRO] <body> tag NÃO encontrada!")

# 5. Verificar estrutura
print("\n[5] Estrutura do HTML:")
print(f"    DOCTYPE: {'SIM' if html.startswith('<!DOCTYPE') else 'NÃO'}")
print(f"    <html>: {'SIM' if '<html' in html else 'NÃO'}")
print(f"    <head>: {'SIM' if '<head>' in html else 'NÃO'}")
print(f"    <body>: {'SIM' if '<body>' in html or '<body ' in html else 'NÃO'}")
print(f"    <main>: {'SIM' if '<main' in html else 'NÃO'}")

# 6. Salvar para análise manual
with open('c:\\projetos\\poker_ranking\\painel_check.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n[6] HTML salvo em: c:\\projetos\\poker_ranking\\painel_check.html")
