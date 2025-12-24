#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament
from core.views.financial import calcular_financeiro_torneio

tournament = Tournament.objects.filter(nome__icontains='QUINTA').first()
result = calcular_financeiro_torneio(tournament)

print("\n" + "="*60)
print(f"FINANCEIRO - {tournament.nome}")
print("="*60)
print(f"\nJogadores:        {result['count_players']}")
print(f"Buy-in Total:     R$ {result['buyin_total']:.2f}")
print(f"Faturamento Bruto: R$ {result['faturamento_bruto']:.2f}")
print(f"  ├─ Buy-in:      R$ {result['buyin_total']:.2f}")
print(f"  ├─ Rebuys/Ads:  R$ {result['produtos_premiacao']:.2f}")
print(f"  └─ Staff:       R$ {result['outros_produtos']:.2f}")
print(f"\nRake Total:       R$ {result['rake_total']:.2f}")
print(f"Pote Total:       R$ {result['pote_total']:.2f}")
print(f"Prêmios Pagos:    R$ {result['premios_pagos']:.2f}")
print(f"Saldo/Lucro:      R$ {result['saldo']:.2f}")
print("="*60 + "\n")
