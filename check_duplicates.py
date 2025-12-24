#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import TournamentResult, Player, Tenant, Tournament
from django.db.models import Count

veris = Tenant.objects.get(slug='veris-poker')
marquinhos = Player.objects.get(id=59, tenant=veris)

# Procurar resultados do Marquinhos
resultados = TournamentResult.objects.filter(
    player=marquinhos,
    tournament__tenant=veris
).select_related('tournament').order_by('-tournament__data')

print('=== RESULTADOS DO MARQUINHOS ===\n')
for i, r in enumerate(resultados, 1):
    data_str = r.tournament.data.strftime("%d/%m/%Y")
    print(f'{i:2d}. {r.tournament.nome:30s} | {data_str} | Pos: {r.posicao} | Premio: R${r.premiacao_recebida:.2f}')

# Procurar por duplicatas (mesmo torneio, mesmo jogador)
print('\n=== VERIFICANDO DUPLICATAS ===\n')

duplicatas = TournamentResult.objects.filter(
    player=marquinhos,
    tournament__tenant=veris
).values('tournament').annotate(count=Count('id')).filter(count__gt=1)

if duplicatas.exists():
    print('ENCONTRADAS DUPLICATAS:')
    for dup in duplicatas:
        t = Tournament.objects.get(id=dup['tournament'])
        results = TournamentResult.objects.filter(player=marquinhos, tournament=t)
        print(f'\n  Torneio: {t.nome} (ID: {t.id})')
        print(f'  Quantidade de registros: {dup["count"]}')
        for r in results:
            print(f'    - ID {r.id}: Posição {r.posicao} | Prêmio R${r.premiacao_recebida:.2f}')
else:
    print('Nenhuma duplicata encontrada.')
