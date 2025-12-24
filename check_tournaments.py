#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Tenant, TournamentResult, Player
from datetime import datetime

veris = Tenant.objects.get(slug='veris-poker')

# Procurar torneios Semanal #1 - Quarta
torneios = Tournament.objects.filter(
    tenant=veris,
    nome__icontains='Semanal #1 - Quarta',
)

print(f'Encontrados {torneios.count()} torneios com nome contendo "Semanal #1 - Quarta":\n')
for t in torneios:
    print(f'ID: {t.id} | Nome: {t.nome} | Data: {t.data} | Tipo: {t.tipo}')

# Ver resultados do Marquinhos nesses torneios
marquinhos = Player.objects.get(id=59, tenant=veris)

print(f'\n=== RESULTADOS DO MARQUINHOS NOS TORNEIOS "SEMANAL #1" ===')
for t in torneios:
    results = TournamentResult.objects.filter(tournament=t, player=marquinhos)
    if results.exists():
        for r in results:
            print(f'\nTorneio ID {t.id} ({t.nome}):')
            print(f'  Posição: {r.posicao}')
            print(f'  Prêmio: R${r.premiacao_recebida:.2f}')
    else:
        print(f'\nTorneio ID {t.id} ({t.nome}): Marquinhos não tem resultado')
