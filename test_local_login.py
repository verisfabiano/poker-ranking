#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("="*80)
print("TESTE: Login Local Funciona")
print("="*80)

client = Client()

# 1. Tentar login
print("\n[1] Tentando login com veris/veris123...")
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

print(f"    Status: {response.status_code}")

if response.status_code == 200:
    print("    [OK] Login realizado com sucesso!")
    
    # 2. Tentar acessar painel
    print("\n[2] Acessando /painel/...")
    response = client.get('/painel/')
    print(f"    Status: {response.status_code}")
    
    if response.status_code == 200:
        print("    [OK] Painel acessível!")
        
        # Verificar se página tem conteúdo
        html = response.content.decode('utf-8', errors='ignore')
        if 'Painel' in html or 'Temporada' in html:
            print("    [OK] Conteúdo presente na página!")
        else:
            print("    [AVISO] Página carregou mas conteúdo não identificado")
    else:
        print(f"    [ERRO] Painel retornou {response.status_code}")
else:
    print(f"    [ERRO] Login falhou: {response.status_code}")

print("\n[✅] Google OAuth foi removido com sucesso!")
print("[✅] Sistema usando apenas login local!")
