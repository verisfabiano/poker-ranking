#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import TournamentProduct

# Ver todos os produtos
produtos = TournamentProduct.objects.all()
print(f'Total de TournamentProducts: {produtos.count()}\n')

for p in produtos:
    print(f'Nome: {p.nome}')
    print(f'  Valor: R$ {p.valor}')
    print(f'  Entra em Premiação: {p.entra_em_premiacao}')
    print(f'  Tenant: {p.tenant}')
    print()
