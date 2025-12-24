#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análise profunda do HTML para entender por que não está renderizando
"""
import os
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("="*80)
print("ANÁLISE PROFUNDA: Por que o conteúdo está em branco?")
print("="*80)

# 1. Fazer login e pegar HTML
client = Client()
print("\n[1] Fazendo login como veris/veris123...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

if response.status_code != 200:
    print(f"[ERRO] Login falhou: {response.status_code}")
    exit(1)

print("[OK] Login realizado com sucesso")

# 2. Acessar /painel/
print("\n[2] GET /painel/")
response = client.get('/painel/')
if response.status_code != 200:
    print(f"[ERRO] /painel/ retornou {response.status_code}")
    exit(1)

html = response.content.decode('utf-8', errors='ignore')
print(f"[OK] Página carregada: {len(html)} bytes")

# 3. Análise do HTML
print("\n[3] ANÁLISE DE ESTRUTURA HTML:")

# DOCTYPE
if html.startswith('<!DOCTYPE'):
    print("    [OK] DOCTYPE presente")
else:
    print("    [ALERTA] DOCTYPE não encontrado no início")

# <head>
if '<head>' in html or '<head ' in html:
    print("    [OK] <head> tag encontrada")
else:
    print("    [ERRO] <head> tag NÃO encontrada")

# <body>
if '<body>' in html or '<body ' in html:
    print("    [OK] <body> tag encontrada")
else:
    print("    [ERRO] <body> tag NÃO encontrada")

# <main>
if '<main' in html:
    print("    [OK] <main> tag encontrada")
    # Procurar conteúdo dentro de main
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if main_match:
        main_content = main_match.group(1)
        print(f"        - Tamanho do conteúdo: {len(main_content)} bytes")
        # Contar elementos
        h1_count = main_content.count('<h1>')
        h2_count = main_content.count('<h2>')
        h3_count = main_content.count('<h3>')
        div_count = main_content.count('<div')
        print(f"        - <h1>: {h1_count}, <h2>: {h2_count}, <h3>: {h3_count}, <div>: {div_count}")
else:
    print("    [ERRO] <main> tag NÃO encontrada")

# 4. ANÁLISE DE CSS
print("\n[4] ANÁLISE DE CSS:")

# Procurar todas as tags <style>
style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
print(f"    Blocos <style>: {len(style_blocks)}")

# Procurar por CSS que pode estar ocultando
problematic_css = {
    'display: none': [],
    'visibility: hidden': [],
    'opacity: 0': [],
    'height: 0': [],
    'width: 0': [],
    'overflow: hidden': [],
}

for style_content in style_blocks:
    for css_rule in problematic_css.keys():
        matches = re.findall(rf'[^{{]*\{{\s*[^}}]*{re.escape(css_rule)}[^}}]*\}}', style_content, re.IGNORECASE)
        problematic_css[css_rule].extend(matches)

print("    CSS Problemático:")
for css_rule, matches in problematic_css.items():
    if matches:
        print(f"        [!] {css_rule}: {len(matches)} ocorrências")
        for match in matches[:2]:  # Mostra os 2 primeiros
            match_clean = match.replace('\n', ' ')[:100]
            print(f"            → {match_clean}...")
    else:
        print(f"        [OK] {css_rule}: Não encontrado")

# 5. ANÁLISE DE <style> DO BOOTSTRAP
print("\n[5] VERIFICAÇÃO DE CDN:")
if 'bootstrap@5.3.0' in html:
    print("    [OK] Bootstrap 5.3.0 está sendo carregado de CDN")
else:
    print("    [ALERTA] Bootstrap 5.3.0 não encontrado na tag <link>")

if 'bootstrap-icons' in html:
    print("    [OK] Bootstrap Icons está sendo carregado de CDN")
else:
    print("    [ALERTA] Bootstrap Icons não encontrado na tag <link>")

# 6. ANÁLISE DE ATRIBUTOS DO <body>
print("\n[6] ANÁLISE DO <body>:")
body_match = re.search(r'<body([^>]*)>', html)
if body_match:
    body_attr = body_match.group(1)
    print(f"    Atributos: {body_attr if body_attr.strip() else '(nenhum)'}")
    print(f"    Classes: {body_attr.count('class=')}")
    print(f"    IDs: {body_attr.count('id=')}")
else:
    print("    <body> não encontrado!")

# 7. ANÁLISE DO <main>
print("\n[7] ANÁLISE DO <main>:")
main_match = re.search(r'<main([^>]*)>', html)
if main_match:
    main_attr = main_match.group(1)
    print(f"    Atributos: {main_attr if main_attr.strip() else '(nenhum)'}")
    if 'class' in main_attr:
        class_match = re.search(r'class=["\']([^"\']*)["\']', main_attr)
        if class_match:
            classes = class_match.group(1).split()
            print(f"    Classes: {classes}")
    if 'style' in main_attr:
        style_match = re.search(r'style=["\']([^"\']*)["\']', main_attr)
        if style_match:
            print(f"    Style inline: {style_match.group(1)}")

# 8. VERIFICAÇÃO DE MODAL
print("\n[8] ANÁLISE DE MODALS:")
modals = re.findall(r'<div[^>]*class="[^"]*modal[^"]*"[^>]*>', html)
print(f"    Modals encontrados: {len(modals)}")

# 9. ANÁLISE DE SCRIPTS
print("\n[9] ANÁLISE DE SCRIPTS:")
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"    <script> tags inline: {len(scripts)}")

# Procurar por scripts que podem estar manipulando o DOM
for i, script in enumerate(scripts):
    if any(word in script.lower() for word in ['innerHTML', 'remove', 'hide', 'display', 'document.body']):
        print(f"    [!] Script {i} contém manipulação de DOM:")
        lines = script.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"        {line.strip()[:80]}")

# 10. VERIFICAÇÃO DE CONTEÚDO VISÍVEL
print("\n[10] ANÁLISE DE CONTEÚDO VISÍVEL:")

# Remover tags HTML
text_only = re.sub(r'<[^>]+>', '', html)
text_only = re.sub(r'\s+', ' ', text_only).strip()
visible_chars = len(text_only)
print(f"    Caracteres visíveis: {visible_chars}")
print(f"    Proporção conteúdo/total: {(visible_chars / len(html)) * 100:.1f}%")

# Procurar por palavras-chave
keywords = ['Painel', 'Temporada', 'Torneio', 'Ranking', 'Dashboard']
print(f"    Palavras-chave encontradas:")
for keyword in keywords:
    count = text_only.count(keyword)
    if count > 0:
        print(f"        - '{keyword}': {count}x")

# 11. VERIFICAÇÃO DE ERROS DE LÓGICA
print("\n[11] VERIFICAÇÃO DE POSSÍVEIS PROBLEMAS:")

# Procurar por condicional que pode estar ocultando main
if '{% if' in html:
    print("    [!] Template tem condicionais Django ({% if %})")
    # Isso é esperado

# Procurar por template que pode estar vazio
if '<main' in html and '<h1>' not in html:
    print("    [ERRO] <main> existe mas não há <h1> nele!")
else:
    print("    [OK] <h1> encontrado depois de <main>")

print("\n" + "="*80)
print("CONCLUSÃO:")
print("="*80)
print("""
Se chegou até aqui e viu [OK] em tudo, significa que:
1. O HTML está sendo gerado corretamente no servidor ✅
2. A estrutura está completa ✅
3. Não há CSS óbvio ocultando o conteúdo ✅

O PROBLEMA ESTÁ NO NAVEGADOR DO USUÁRIO:
- Talvez Bootstrap CSS não está carregando do CDN
- Talvez extensão do navegador está bloqueando conteúdo
- Talvez há erro de JavaScript no console
- Talvez cache esteja servindo página velha
- Talvez zoom do navegador esteja muito baixo

PRÓXIMAS AÇÕES:
1. Peça ao usuário para abrir F12 (DevTools)
2. Vá para Console e procure por ERROS (vermelho)
3. Vá para Network e veja se Bootstrap CSS retornou 200 OK
4. Limpe o cache (Ctrl+Shift+Delete)
5. Tente em navegador privado (Ctrl+Shift+P)
6. Tente em outro navegador (Firefox, Edge)
""")
