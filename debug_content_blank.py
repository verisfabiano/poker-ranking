#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 80)
print("DEBUG: Renderizacao do Conteudo do Painel")
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

print(f"Status: {response.status_code}")
print(f"Content-Length: {len(content)} bytes")

# Procurar pela tag <main>
main_start = content.find('<main')
if main_start != -1:
    main_end = content.find('</main>', main_start)
    if main_end != -1:
        main_content = content[main_start:main_end+7]
        print(f"\n[3] Conteudo da tag <main>:")
        print(f"    Tamanho: {len(main_content)} bytes")
        
        # Procurar por container-fluid
        if 'container-fluid' in main_content:
            print("    [OK] container-fluid encontrado")
            
            # Procurar por page-header
            if 'page-header' in main_content:
                print("    [OK] page-header encontrado")
            else:
                print("    [FALTA] page-header NOT encontrado")
            
            # Procurar por ranking-hero
            if 'ranking-hero' in main_content:
                print("    [OK] ranking-hero encontrado")
            else:
                print("    [FALTA] ranking-hero NOT encontrado")
            
            # Procurar por season-card ou Temporadas
            if 'season-card' in main_content:
                print("    [OK] season-card encontrado")
            elif 'Suas Temporadas' in main_content:
                print("    [OK] 'Suas Temporadas' encontrado")
            else:
                print("    [FALTA] Nenhum season-card ou 'Suas Temporadas'")
            
            # Procurar por onboarding (se nao tem temporadas)
            if 'Bem-vindo ao PokerClube' in main_content:
                print("    [OK] Seção onboarding encontrada (sem temporadas?)")
            elif 'Criar Temporada' in main_content or 'Acesso Rápido' in main_content:
                print("    [OK] Seções esperadas encontradas")
            else:
                print("    [ALERTA] Nenhuma seção principal encontrada")
            
            # Ver o HTML bruto da main
            print(f"\n[4] Primeiros 1500 caracteres da <main>:")
            print("    " + "=" * 76)
            for line in main_content[:1500].split('\n')[:30]:
                print(f"    {line}")
            print("    " + "=" * 76)
        else:
            print("    [ERRO] container-fluid NOT encontrado!")
else:
    print("[ERRO] Tag <main> nao encontrada!")

# Procurar por erros no HTML
print(f"\n[5] Verificacoes de erro:")
if 'error' in content.lower():
    print("    [ALERTA] Palavra 'error' encontrada no HTML")
if 'exception' in content.lower():
    print("    [ALERTA] Palavra 'exception' encontrada no HTML")
if '500' in content:
    print("    [ALERTA] '500' encontrado no HTML")

# Verificar se há conteúdo entre as tags
content_area = content[content.find('<main'):content.find('</main')]
if len(content_area) < 500:
    print(f"    [ALERTA] Conteudo dentro de <main> parece muito pequeno: {len(content_area)} bytes")
else:
    print(f"    [OK] Conteudo dentro de <main> tem tamanho OK: {len(content_area)} bytes")
