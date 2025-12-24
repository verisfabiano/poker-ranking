#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Player, TournamentProduct, PlayerProductPurchase
from django.db.models import Sum

# Buscar um torneio que tenha inscrições
tournament = Tournament.objects.filter(permite_rebuy=True).first()

if tournament:
    print(f'✓ Torneio encontrado: {tournament.nome}')
    
    # Ver quantos produtos tem
    products = TournamentProduct.objects.filter(tenant=tournament.tenant)
    print(f'✓ Total de TournamentProducts: {products.count()}')
    
    # Ver compras
    purchases = PlayerProductPurchase.objects.filter(tournament=tournament)
    print(f'✓ Total de PlayerProductPurchase: {purchases.count()}')
    
    total_valor = purchases.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
    print(f'✓ Valor total: R$ {total_valor:.2f}')
    
    # Listar os produtos
    for p in purchases:
        print(f'  - {p.player.nome}: {p.product.nome} x{p.quantidade} = R$ {p.valor_pago}')
else:
    print('✗ Nenhum torneio com rebuy encontrado')

print('\n=== Testando lógica de cálculo financeiro ===')

# Agora testar a função de cálculo financeiro
from core.views.financial import calcular_financeiro_torneio

for tournament in Tournament.objects.all()[:3]:
    print(f'\nTorneio: {tournament.nome}')
    result = calcular_financeiro_torneio(tournament)
    print(f'  Buy-in Total: R$ {result.get("buyin_total", 0):.2f}')
    print(f'  Produtos Premiacao: R$ {result.get("produtos_premiacao", 0):.2f}')
    print(f'  Total Produtos: R$ {result.get("total_produtos", 0):.2f}')
