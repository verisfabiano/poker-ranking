#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, PlayerProductPurchase
from core.views.financial import calcular_financeiro_torneio
from decimal import Decimal
from django.db.models import Sum

# Pegar torneio específico
tournament = Tournament.objects.filter(nome__icontains='QUINTA INSACA').first()

if tournament:
    fin = calcular_financeiro_torneio(tournament)
    
    # Contar quantidade de rebuys e addons
    rebuys_count = PlayerProductPurchase.objects.filter(
        tournament=tournament, product__nome__icontains='rebuy'
    ).count()
    addons_count = PlayerProductPurchase.objects.filter(
        tournament=tournament, product__nome__icontains='addon'
    ).count()
    
    # Somar valores separados
    rebuys_value = PlayerProductPurchase.objects.filter(
        tournament=tournament, product__nome__icontains='rebuy'
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    addons_value = PlayerProductPurchase.objects.filter(
        tournament=tournament, product__nome__icontains='addon'
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    staff_value = PlayerProductPurchase.objects.filter(
        tournament=tournament, product__nome__icontains='staff'
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    # Faturamento bruto
    faturamento_bruto = fin['buyin_total'] + fin['produtos_premiacao'] + fin['outros_produtos']
    
    # Lucro
    lucro = faturamento_bruto - fin['premios_pagos']
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         DASHBOARD FINANCEIRO                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

DATA              | 19/12/2025
TORNEIO           | {tournament.nome}
JOGADORES         | {fin['count_players']}
─────────────────────────────────────────────────────────────────────────────

BREAKDOWN DE FATURAMENTO:
─────────────────────────────────────────────────────────────────────────────
Buy-in            | R$ {fin['buyin_total']:>10.2f}
Rebuys ({rebuys_count}x)        | R$ {rebuys_value:>10.2f}
Add-ons ({addons_count}x)        | R$ {addons_value:>10.2f}
Staff             | R$ {staff_value:>10.2f}
─────────────────────────────────────────────────────────────────────────────
FATURAMENTO BRUTO | R$ {faturamento_bruto:>10.2f}  ← TOTAL ARRECADADO
─────────────────────────────────────────────────────────────────────────────

ANÁLISE DE LUCRO:
─────────────────────────────────────────────────────────────────────────────
Rake/Taxa         | R$ {fin['rake_total']:>10.2f}
Premiação Paga    | R$ {fin['premios_pagos']:>10.2f}
─────────────────────────────────────────────────────────────────────────────
LUCRO DO TORNEIO  | R$ {lucro:>10.2f}
─────────────────────────────────────────────────────────────────────────────

STATUS: ✅ Layout atualizado com sucesso!
""")
else:
    print("Torneio não encontrado")
