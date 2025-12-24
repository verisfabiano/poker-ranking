#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import TournamentResult, Player, Tenant

veris = Tenant.objects.get(slug='veris-poker')
marquinhos = Player.objects.get(id=59, tenant=veris)

# Pegar os dois resultados "Semanal #1 - Quarta"
resultados = TournamentResult.objects.filter(
    player=marquinhos,
    tournament__tenant=veris,
    tournament__nome__icontains='Semanal #1 - Quarta'
).select_related('tournament').order_by('id')

print(f'Encontrados {resultados.count()} resultados para Semanal #1\n')

for i, r in enumerate(resultados):
    print(f'{i+1}. ID {r.id} | Torneio ID {r.tournament.id} | Pos: {r.posicao} | Premio: R${r.premiacao_recebida}')

# Se houver mais de um, manter apenas o de maior prêmio
if resultados.count() > 1:
    print('\nRemocionando resultado duplicado...')
    # Remover o de menor prêmio (Pos 7, prêmio 0)
    resultado_ruim = resultados.filter(posicao=7, premiacao_recebida=0).first()
    if resultado_ruim:
        print(f'Removendo: ID {resultado_ruim.id} | Pos {resultado_ruim.posicao} | Premio {resultado_ruim.premiacao_recebida}')
        resultado_ruim.delete()
        print('✓ Removido com sucesso')
