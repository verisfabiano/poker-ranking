#!/usr/bin/env python
"""
Teste real da view player_progress_season acessando como se fosse pelo navegador
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from core.models import Season, Player, Tenant

# Setup
client = Client()

# Obter dados de teste
veris = Tenant.objects.get(slug='veris-poker')
season = Season.objects.filter(tenant=veris, id=12).first()
player = Player.objects.filter(tenant=veris, id=54).first()

print(f"\n{'='*60}")
print("TESTE REAL - SIMULANDO NAVEGADOR")
print(f"{'='*60}\n")

if season and player:
    url = f'/jogador/{player.id}/season/{season.id}/evolucao/'
    print(f"URL: {url}\n")
    
    response = client.get(url, follow=True)  # follow=True para seguir redirects
    
    print(f"Status: {response.status_code}")
    print(f"URL Final: {response.request['PATH_INFO']}")
    
    # Mostrar primeiras 500 chars do conteúdo
    content = response.content.decode('utf-8', errors='ignore')
    
    if response.status_code == 200:
        print("\n✓ 200 OK - Página renderizada")
        if 'Evolução' in content:
            print("✓ Template 'Evolução' encontrado no conteúdo")
        if 'Joãozinho' in content:
            print("✓ Nome do jogador encontrado")
            
        # Procurar por erros no HTML
        if 'error' in content.lower() or 'exception' in content.lower():
            print("\n⚠ Possível erro no HTML:")
            # Mostrar linha com erro
            for i, line in enumerate(content.split('\n')):
                if 'error' in line.lower() or 'exception' in line.lower():
                    print(f"  Linha {i}: {line[:100]}")
    else:
        print(f"\n✗ Erro {response.status_code}")
        print(f"Conteúdo: {content[:500]}")

print(f"\n{'='*60}\n")
