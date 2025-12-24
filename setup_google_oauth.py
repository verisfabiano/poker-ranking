#!/usr/bin/env python
"""
Script para configurar Google OAuth no Django Admin
Usage: python setup_google_oauth.py <client_id> <client_secret>
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_google_oauth(client_id, client_secret, site_id=1):
    """
    Configura Google OAuth no Django
    
    Args:
        client_id: Client ID do Google Console
        client_secret: Client Secret do Google Console
        site_id: ID do site (padrão: 1)
    """
    try:
        # Obter ou criar o site
        site = Site.objects.get(id=site_id)
        print(f"✓ Site encontrado: {site.domain}")
    except Site.DoesNotExist:
        print(f"✗ Site com id {site_id} não encontrado")
        print("  Criando site padrão...")
        site = Site.objects.create(
            id=site_id,
            domain='localhost:8000',
            name='Poker Ranking'
        )
        print(f"✓ Site criado: {site.domain}")
    
    # Verificar se já existe uma aplicação Google
    try:
        app = SocialApp.objects.get(provider='google')
        print(f"✓ Aplicação Google já existe")
        
        # Atualizar credenciais
        app.client_id = client_id
        app.secret = client_secret
        app.save()
        print(f"✓ Credenciais atualizadas")
        
    except SocialApp.DoesNotExist:
        print(f"  Criando aplicação Google OAuth...")
        app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id=client_id,
            secret=client_secret
        )
        print(f"✓ Aplicação Google criada")
    
    # Associar site à aplicação
    if site not in app.sites.all():
        app.sites.add(site)
        print(f"✓ Site associado à aplicação")
    
    print("\n" + "="*50)
    print("✅ Google OAuth Configurado com Sucesso!")
    print("="*50)
    print(f"Provider: google")
    print(f"Client ID: {client_id[:20]}...")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Site: {site.domain}")
    print(f"\nURLs de Autenticação:")
    print(f"  - Login: http://{site.domain}/accounts/login/")
    print(f"  - Signup: http://{site.domain}/accounts/signup/")
    print(f"  - Google Callback: http://{site.domain}/accounts/google/login/callback/")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python setup_google_oauth.py <client_id> <client_secret>")
        print("\nExemplo:")
        print("  python setup_google_oauth.py 'seu_client_id' 'seu_client_secret'")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    
    if len(sys.argv) > 3:
        site_id = int(sys.argv[3])
    else:
        site_id = 1
    
    setup_google_oauth(client_id, client_secret, site_id)
