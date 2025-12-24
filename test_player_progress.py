#!/usr/bin/env python
"""
Teste para verificar a view player_progress_season
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from core.models import Season, Player, Tenant, TenantUser
from core.views.player import player_progress_season

# Setup
client = Client()
factory = RequestFactory()

# Obter dados de teste
veris = Tenant.objects.get(slug='veris-poker')
season = Season.objects.filter(tenant=veris, id=12).first()  # Temporada 2024
player = Player.objects.filter(tenant=veris, id=54).first()  # Joãozinho

print(f"\n{'='*60}")
print("TESTE player_progress_season")
print(f"{'='*60}\n")

# Dados
print(f"Season: {season}")
print(f"Player: {player}")
print(f"Tenant: {veris}\n")

if season and player:
    # Procurar um user para fazer login
    tenant_users = TenantUser.objects.filter(tenant=veris)
    print(f"Tenant Users: {tenant_users.count()}")
    
    if tenant_users.exists():
        # Usar o primeiro usuário do tenant
        tu = tenant_users.first()
        user = tu.user
        print(f"User para teste: {user.username}\n")
        
        # Fazer login
        if client.login(username=user.username, password=user.username):  # Assume senha = username
            print("✓ Login bem-sucedido\n")
        else:
            print("✗ Login falhou\n")
            # Tentar com um usuário admin
            admin = User.objects.filter(is_staff=True).first()
            if admin:
                print(f"Tentando com admin: {admin.username}")
                if client.login(username=admin.username, password=admin.username):
                    print("✓ Login com admin bem-sucedido")
                else:
                    print("✗ Login com admin falhou")
        
        # Fazer requisição
        print(f"\nAcessando URL: /jogador/{player.id}/season/{season.id}/evolucao/\n")
        response = client.get(f'/jogador/{player.id}/season/{season.id}/evolucao/')
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.get('content-type')}")
        
        if response.status_code == 302:
            print(f"Redirect Location: {response.url}")
            # Ver o que mensagens foram adicionadas
            if response.wsgi_request:
                storage = list(response.wsgi_request._messages)
                if storage:
                    print(f"\nMensagens:")
                    for msg in storage:
                        print(f"  - {msg}")
        
        elif response.status_code == 200:
            print("\n✓ Página renderizada com sucesso!")
            # Procurar por "Evolução" no conteúdo
            if b'Evolu' in response.content:
                print("✓ Template player_progress.html foi renderizado")
            else:
                print("? Template pode não ser o esperado")
        
        else:
            print(f"\n✗ Erro na resposta: {response.status_code}")
else:
    print("✗ Não foi possível obter season ou player de teste")

print(f"\n{'='*60}\n")
