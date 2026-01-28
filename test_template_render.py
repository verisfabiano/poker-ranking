import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Season, Tenant

c = Client()

# Criar ou pegar usuário admin
admin_user = User.objects.filter(is_staff=True).first()
if admin_user:
    print(f"Admin user found: {admin_user.username}")
    
    # Pegar qualquer season
    season = Season.objects.first()
    if season:
        print(f"Season found: {season.nome} (ID: {season.id})")
        # Login
        c.force_login(admin_user)
        
        r = c.get(f'/season/{season.id}/torneios/novo/')
        print(f"Status: {r.status_code}")
        print(f"Content length: {len(r.content)}")
        print("\n--- Checking for content ---\n")
        content = r.content.decode('utf-8', errors='ignore')
        
        # Procurar pelo header do wizard
        if "Criar Novo Torneio" in content:
            print("✓ Found 'Criar Novo Torneio'")
        else:
            print("✗ NOT FOUND 'Criar Novo Torneio'")
            
        if "Abrir Assistente Guiado" in content:
            print("✓ Found 'Abrir Assistente Guiado'")
        else:
            print("✗ NOT FOUND 'Abrir Assistente Guiado'")
            
        if "wizardTournamentModal" in content:
            print("✓ Found modal element")
        else:
            print("✗ NOT FOUND modal element")
            
        # Print status and length
        print(f"\nStatus Code: {r.status_code}")
        if r.status_code == 200:
            print("✓ Page loaded successfully")
        else:
            print(f"✗ Error: {r.status_code}")
    else:
        print("No season found")
else:
    print("No admin user found")
