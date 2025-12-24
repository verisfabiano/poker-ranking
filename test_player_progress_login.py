#!/usr/bin/env python
"""
Teste para verificar a view player_progress_season COM LOGIN
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from core.models import Season, Player, Tenant

# Setup
client = Client()

# Obter dados de teste
veris = Tenant.objects.get(slug='veris-poker')
season = Season.objects.filter(tenant=veris, id=12).first()  # Temporada 2024
player = Player.objects.filter(tenant=veris, id=54).first()  # Joãozinho

print(f"\n{'='*60}")
print("TESTE player_progress_season COM LOGIN")
print(f"{'='*60}\n")

# Dados
print(f"Season: {season.nome if season else 'Não encontrada'} (ID: {season.id if season else '?'})")
print(f"Player: {player.apelido or player.nome if player else 'Não encontrado'} (ID: {player.id if player else '?'})")
print(f"Tenant: {veris.nome}\n")

if season and player:
    # Login com testevris
    print("Tentando login com testevris / testevris123...")
    login_success = client.login(username='testevris', password='testevris123')
    
    if login_success:
        print("✓ Login bem-sucedido!\n")
        
        # Fazer requisição
        url = f'/jogador/{player.id}/season/{season.id}/evolucao/'
        print(f"Acessando URL: {url}\n")
        response = client.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.get('content-type')}")
        
        if response.status_code == 302:
            print(f"Redirect Location: {response.url}")
            
        elif response.status_code == 200:
            print("\n✓ Página renderizada com sucesso!")
            # Procurar por "Evolução" no conteúdo
            content_str = response.content.decode('utf-8', errors='ignore')
            if 'Evolu' in content_str:
                print("✓ Template player_progress.html foi renderizado")
                if 'Joãozinho' in content_str:
                    print("✓ Nome do jogador encontrado no template")
                if 'Temporada 2024' in content_str:
                    print("✓ Nome da temporada encontrado no template")
            else:
                print("? Template pode não ser o esperado")
        else:
            print(f"\n✗ Erro na resposta: {response.status_code}")
    else:
        print("✗ Login falhou")

else:
    print("✗ Não foi possível obter season ou player de teste")

print(f"\n{'='*60}\n")
