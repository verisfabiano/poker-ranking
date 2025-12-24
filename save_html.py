#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 80)
print("TESTE: Salvando HTML completo para analise manual")
print("=" * 80)

client = Client()

# Login
print("\n[1] Fazendo login...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# Acessar /painel/
print("[2] GET /painel/")
response = client.get('/painel/')
content = response.content.decode('utf-8', errors='ignore')

# Salvar em arquivo
with open('c:\\projetos\\poker_ranking\\painel_output.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[3] HTML salvo em: c:\\projetos\\poker_ranking\\painel_output.html")
print(f"    Tamanho: {len(content)} bytes")

# Também analisar elementos
print(f"\n[4] Analise rapida:")

# Procurar por container-fluid e seu conteúdo
main_start = content.find('<main')
main_end = content.find('</main>')

if main_start >= 0 and main_end >= 0:
    main_html = content[main_start:main_end]
    
    # Procurar por divs vazias
    import re
    empty_divs = re.findall(r'<div[^>]*>\s*</div>', main_html)
    if empty_divs:
        print(f"    [ALERTA] {len(empty_divs)} divs vazias encontradas")
    
    # Procurar por elementos
    if '<h1>' in main_html or '<h2>' in main_html:
        print(f"    [OK] Headings encontrados")
    
    if 'season-card' in main_html:
        print(f"    [OK] Season cards encontrados")
        season_count = main_html.count('season-card')
        print(f"        {season_count} cards")
    
    # Procurar por divs com style que poderia ocultcr
    hidden_divs = re.findall(r'<div[^>]*style="[^"]*display\s*:\s*none[^"]*"', main_html)
    if hidden_divs:
        print(f"    [ALERTA] {len(hidden_divs)} divs com 'display: none' encontrados")
        for div in hidden_divs[:3]:
            print(f"        {div[:100]}")
    else:
        print(f"    [OK] Nenhum div com 'display: none'")

print(f"\n[5] Abra o arquivo em um editor de texto para inspecionar manualmente!")
