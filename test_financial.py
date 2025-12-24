#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Tenant
from core.views.financial import calcular_financeiro_torneio

tenant = Tenant.objects.get(slug='espacopoker')
tournaments = Tournament.objects.filter(tenant=tenant).order_by('-data')

print("=== TESTE DE CÁLCULO FINANCEIRO ===\n")

for t in tournaments:
    fin = calcular_financeiro_torneio(t)
    print(f"Torneio: {t.nome}")
    print(f"  Jogadores: {fin['count_players']}")
    print(f"  Buy-in Total: R${fin['buyin_total']:.2f}")
    print(f"  Rake: R${fin['rake_total']:.2f}")
    print(f"  Pote: R${fin['pote_total']:.2f}")
    print(f"  Produtos: R${fin['produtos_vendidos']:.2f}")
    print(f"  Prêmios Pagos: R${fin['premios_pagos']:.2f}")
    print(f"  Saldo: R${fin['saldo']:.2f}")
    print()
