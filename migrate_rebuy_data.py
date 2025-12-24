#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import TournamentPlayerPurchase, PlayerProductPurchase, TournamentProduct
from django.db.models import Sum

# Verificar dados em TournamentPlayerPurchase (tabela antiga)
old_purchases = TournamentPlayerPurchase.objects.all()
print(f'Total de registros em TournamentPlayerPurchase (ANTIGA): {old_purchases.count()}')

for purchase in old_purchases:
    print(f'  - {purchase.tournament.nome} / {purchase.player.nome}: {purchase.tipo} x{purchase.quantidade} = R$ {purchase.valor_total}')

if old_purchases.count() > 0:
    print('\n⚠️  MIGRAÇÃO NECESSÁRIA: Há dados antigos em TournamentPlayerPurchase!')
    print('Vou migrar agora...\n')
    
    migrado_count = 0
    for old_purchase in old_purchases:
        # Criar ou obter TournamentProduct para este tipo
        product, created = TournamentProduct.objects.get_or_create(
            nome=old_purchase.tipo,
            tenant=old_purchase.tournament.tenant,
            defaults={
                'descricao': f'{old_purchase.tipo.replace("_", " ").title()} - Migrado',
                'valor': old_purchase.valor,
                'entra_em_premiacao': old_purchase.tipo in ['REBUY', 'REBUY_DUPLO', 'ADDON']
            }
        )
        
        # Criar em PlayerProductPurchase
        new_purchase, created = PlayerProductPurchase.objects.get_or_create(
            tournament=old_purchase.tournament,
            player=old_purchase.player,
            product=product,
            defaults={
                'tenant': old_purchase.tournament.tenant,
                'quantidade': old_purchase.quantidade,
                'valor_pago': old_purchase.valor_total
            }
        )
        
        if created:
            migrado_count += 1
            print(f'✓ Migrado: {old_purchase.player.nome} - {old_purchase.tipo}')
        else:
            print(f'⊘ Já existia: {old_purchase.player.nome} - {old_purchase.tipo}')
    
    print(f'\n✅ {migrado_count} registros migrados com sucesso!')
else:
    print('✓ Nenhum dado antigo em TournamentPlayerPurchase')
