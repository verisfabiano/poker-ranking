#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
import re

print("=" * 80)
print("DIAGNOSTICO: Analisando /torneios/dashboard/ que retorna 200")
print("=" * 80)

client = Client()

# Login
print("\n[1] Fazendo login...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# Acessar /torneios/dashboard/
print("[2] GET /torneios/dashboard/")
response = client.get('/torneios/dashboard/')
content = response.content.decode('utf-8', errors='ignore')

print(f"    Status: {response.status_code}")
print(f"    Content-Length: {len(content)} bytes")

# Procurar por conteúdo visível
print("\n[3] Analisando conteúdo:")

# Procurar por tags visíveis
visible_content = content.replace('<', '\n<').replace('>', '>\n')
# Remover HTML tags
text_only = re.sub(r'<[^>]+>', '', content)
# Remover espaços em branco
text_only = re.sub(r'\s+', ' ', text_only).strip()

print(f"    Texto visível (sem tags): {len(text_only)} caracteres")
print(f"    Primeiros 200 chars de texto: {text_only[:200]}")

# Procurar por CSS que pode estar ocultando
print("\n[4] Verificando CSS que poderia ocular conteúdo:")

css_issues = [
    ('color: white', 'Texto branco (pode estar invisível em fundo branco)'),
    ('color:#fff', 'Texto branco hex (pode estar invisível)'),
    ('color: #ffffff', 'Texto branco completo'),
    ('display: none', 'Display none (oculta elementos)'),
    ('visibility: hidden', 'Visibility hidden (oculta elementos)'),
    ('opacity: 0', 'Opacity zero (invisível)'),
    ('height: 0', 'Height zero (sem altura)'),
    ('width: 0', 'Width zero (sem largura)'),
    ('font-size: 0', 'Font size zero (texto invisível)'),
]

for css, desc in css_issues:
    if css in content:
        count = content.count(css)
        # Procurar contexto
        idx = content.find(css)
        start = max(0, idx - 100)
        end = min(len(content), idx + 100)
        context = content[start:end]
        
        print(f"\n    [ALERTA] {desc}")
        print(f"    Encontrado {count}x")
        print(f"    Contexto: ...{context}...")

# Procurar especificamente por body style
body_start = content.find('<body')
if body_start != -1:
    body_end = content.find('>', body_start)
    body_tag = content[body_start:body_end+1]
    print(f"\n[5] Tag <body>:")
    print(f"    {body_tag}")
    
    if 'style=' in body_tag:
        print("    [ALERTA] Body tem inline style! Pode estar ocultando conteúdo")

# Procurar por main style
main_start = content.find('<main')
if main_start != -1:
    main_end = content.find('>', main_start)
    main_tag = content[main_start:main_end+1]
    print(f"\n[6] Tag <main>:")
    print(f"    {main_tag}")

# Procurar por container-fluid style
if 'container-fluid' in content:
    idx = content.find('container-fluid')
    start = max(0, idx - 50)
    end = min(len(content), idx + 150)
    context = content[start:end]
    print(f"\n[7] Container-fluid context:")
    print(f"    {context}")

print(f"\n[8] Conclusao:")
if len(text_only) < 100:
    print(f"    [CRITICO] Muito pouco texto visível! Conteúdo pode estar completamente oculto")
elif 'color: white' in content or 'color:#fff' in content:
    print(f"    [PROVAVEL] Texto branco encontrado - pode ser invisível em fundo branco")
else:
    print(f"    [OK] Conteúdo parece estar presente e visível")
