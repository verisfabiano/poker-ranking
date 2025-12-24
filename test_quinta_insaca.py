#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, PlayerProductPurchase
from core.views.financial import calcular_financeiro_torneio

# Procurar especificamente por QUINTA INSACA
tournament = Tournament.objects.filter(nome__icontains='QUINTA').first()

if tournament:
    print(f'\n{"="*60}')
    print(f'Testando: {tournament.nome}')
    print(f'{"="*60}\n')
    
    # Mostrar os produtos deste torneio
    purchases = PlayerProductPurchase.objects.filter(tournament=tournament).select_related('product')
    print(f'Total de compras: {purchases.count()}')
    for p in purchases:
        print(f'  - {p.player.nome}: {p.product.nome} x{p.quantidade} = R$ {p.valor_pago} (entra_em_premiacao={p.product.entra_em_premiacao})')
    
    print(f'\n{"="*60}')
    print('Calculando Financeiro...')
    print(f'{"="*60}\n')
    
    result = calcular_financeiro_torneio(tournament)
    
    print(f'\n{"="*60}')
    print('RESULTADO DO CÁLCULO:')
    print(f'{"="*60}')
    print(f'Buy-in Total:        R$ {result.get("buyin_total", 0):.2f}')
    print(f'Produtos Premiação:  R$ {result.get("total_produtos_premiacao", 0):.2f}')
    print(f'Rake Total:          R$ {result.get("rake_total", 0):.2f}')
    print(f'Pote Total:          R$ {result.get("pote_total", 0):.2f}')
    print(f'Prêmios:             R$ {result.get("total_premios", 0):.2f}')
    print(f'Lucro:               R$ {result.get("lucro", 0):.2f}')
else:
    print('Torneio não encontrado')
