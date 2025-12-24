#!/usr/bin/env python
"""
Script para listar os IDs de todos os torneios e suas informações.
Útil para acessar URLs específicas de detalhes de torneios.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Tenant

def listar_torneios():
    """Lista todos os torneios com seus IDs"""
    
    tenant = Tenant.objects.filter(slug='clube-teste').first()
    
    if not tenant:
        print("❌ Tenant 'Clube Poker Teste' não encontrado!")
        return
    
    print("\n" + "="*90)
    print(f"  LISTA DE TORNEIOS - {tenant.nome}")
    print("="*90 + "\n")
    
    torneios = Tournament.objects.filter(tenant=tenant).order_by('season', '-data')
    
    if not torneios:
        print("Nenhum torneio encontrado.")
        return
    
    for torneio in torneios:
        print(f"ID: {torneio.id:2d} | {torneio.nome:30s} | {torneio.data.strftime('%d/%m/%Y')} | "
              f"Temporada: {torneio.season.nome}")
        print(f"         URL: http://localhost:8000/torneio/{torneio.id}/financeiro/")
        print()
    
    print("="*90)
    print(f"Total de torneios: {torneios.count()}\n")

if __name__ == '__main__':
    listar_torneios()
