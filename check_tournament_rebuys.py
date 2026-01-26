#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament

# Get the tournament from the screenshot (Clube Jaguara, tournament 43)
tournament = Tournament.objects.filter(id=43).first()

if tournament:
    print(f"Tournament: {tournament.nome} (ID: {tournament.id})")
    print(f"Status: {tournament.status}")
    print(f"Permite Rebuy: {tournament.permite_rebuy}")
    print(f"Rebuy Valor: {tournament.rebuy_valor}")
    print(f"Permite Rebuy Duplo: {tournament.permite_rebuy_duplo}")
    print(f"Rebuy Duplo Valor: {tournament.rebuy_duplo_valor}")
    print(f"Permite Add-on: {tournament.permite_addon}")
    print(f"Add-on Valor: {tournament.addon_valor}")
    print(f"Staff Valor: {tournament.staff_valor}")
    print(f"Staff Obrigatório: {tournament.staff_obrigatorio}")
else:
    print("Tournament not found")
    # List all tournaments
    print("\nAvailable tournaments:")
    for t in Tournament.objects.all()[:10]:
        print(f"  - {t.id}: {t.nome} (Status: {t.status})")
