#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import TournamentProduct, Tenant
from decimal import Decimal

# Buscar tenant espacopoker
tenant = Tenant.objects.get(slug='espacopoker')

# Produtos padrão
produtos = [
    {
        'nome': 'Jack Pot',
        'descricao': 'Participação no Jack Pot (OPCIONAL)',
        'valor': Decimal('50.00'),
        'entra_em_premiacao': False,
    },
    {
        'nome': 'Staff',
        'descricao': 'Taxa de Staff/Dealer (OBRIGATÓRIO)',
        'valor': Decimal('30.00'),
        'entra_em_premiacao': False,
    },
    {
        'nome': 'Bounty',
        'descricao': 'Prêmio Bounty (OPCIONAL)',
        'valor': Decimal('25.00'),
        'entra_em_premiacao': False,
    },
    {
        'nome': 'Rebuy',
        'descricao': 'Compra adicional de fichas',
        'valor': Decimal('50.00'),
        'entra_em_premiacao': True,
    },
    {
        'nome': 'Add-on',
        'descricao': 'Compra adicional de fichas no intervalo final',
        'valor': Decimal('50.00'),
        'entra_em_premiacao': True,
    },
]

print("=== CRIANDO PRODUTOS PADRÃO ===\n")

for p in produtos:
    premiacao_text = "💰 Entra em Premiação" if p.get('entra_em_premiacao') else "🎯 Não entra"
    product, created = TournamentProduct.objects.get_or_create(
        nome=p['nome'],
        tenant=tenant,
        defaults={
            'descricao': p['descricao'],
            'valor': p['valor'],
            'entra_em_premiacao': p.get('entra_em_premiacao', False)
        }
    )
    
    if created:
        print(f"✅ Criado: {product.nome} - R${product.valor:.2f} ({premiacao_text})")
    else:
        print(f"⏭️  Existente: {product.nome} - R${product.valor:.2f} ({premiacao_text})")

print(f"\n✨ Total de produtos: {TournamentProduct.objects.filter(tenant=tenant).count()}")
