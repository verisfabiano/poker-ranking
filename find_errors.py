#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
import re

print("=" * 80)
print("DEBUG: Procurando por 'error' no HTML")
print("=" * 80)

client = Client()

# Login
print("\n[1] Fazendo login...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# Acessar painel
print("[2] Acessando /painel/...")
response = client.get('/painel/')
content = response.content.decode('utf-8', errors='ignore')

# Procurar por 'error' (case insensitive)
matches = re.finditer(r'error', content, re.IGNORECASE)
count = 0

print("\n[3] Locais onde 'error' aparece:")
for match in matches:
    count += 1
    start = max(0, match.start() - 100)
    end = min(len(content), match.end() + 100)
    context = content[start:end]
    
    print(f"\n    Ocorrência {count}:")
    print(f"    {context}")
    print("    " + "-" * 76)

if count == 0:
    print("    Nenhuma ocorrência de 'error' encontrada!")
else:
    print(f"\n    Total: {count} ocorrências")
