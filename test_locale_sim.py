#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament

# Get tournament 43
tournament = Tournament.objects.get(id=43)

# Simulate what JavaScript will do
rebuy_str = f"{tournament.rebuy_valor:.2f}".replace('.', ',')  # Simula pt-br locale
print(f"Tournament Rebuy Valor (raw): {tournament.rebuy_valor}")
print(f"With pt-br locale, Django renders as string: '{rebuy_str}'")
print(f"JavaScript: parseFloat('{rebuy_str}'.replace(',', '.')) -> parseFloat('{rebuy_str.replace(',', '.')}')")
print(f"Result in JavaScript: {float(rebuy_str.replace(',', '.'))}")

# Check all rebuy fields
print("\n=== All Rebuy Values ===")
print(f"Rebuy: {tournament.rebuy_valor} (rendered: '{tournament.rebuy_valor}'.replace(',', '.') → {tournament.rebuy_valor})")
print(f"Rebuy Duplo: {tournament.rebuy_duplo_valor} → parseFloat to {float(tournament.rebuy_duplo_valor)}")
print(f"Add-on: {tournament.addon_valor} → parseFloat to {float(tournament.addon_valor)}")
print(f"Permite Rebuy: {tournament.permite_rebuy}")
print(f"Permite Rebuy Duplo: {tournament.permite_rebuy_duplo}")
print(f"Permite Add-on: {tournament.permite_addon}")
