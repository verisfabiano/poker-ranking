#!/usr/bin/env python
"""
Script para criar torneios de teste e lançar resultados.
Executa: python create_test_tournaments.py
"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import (
    Season, Tournament, TournamentEntry, TournamentResult, 
    Player, TournamentType, Tenant
)

print("=" * 70)
print("CRIANDO TORNEIOS DE TESTE E LANÇANDO RESULTADOS")
print("=" * 70)

# Pegar a temporada "Temporada Teste"
try:
    season = Season.objects.get(nome="Temporada Teste")
    print(f"\n✓ Temporada encontrada: {season.nome}")
except Season.DoesNotExist:
    print("\n❌ Temporada 'Temporada Teste' não encontrada!")
    exit(1)

# Pegar o tenant "Veris Poker"
try:
    tenant = Tenant.objects.get(nome="Veris Poker")
    print(f"✓ Tenant encontrado: {tenant.nome}")
except Tenant.DoesNotExist:
    print("❌ Tenant 'Veris Poker' não encontrado!")
    exit(1)

# Pegar o tipo de torneio
try:
    tournament_type = TournamentType.objects.get(nome="Quinta", tenant=tenant)
except TournamentType.DoesNotExist:
    tournament_type = TournamentType.objects.first()
    if not tournament_type:
        print("❌ Nenhum tipo de torneio encontrado!")
        exit(1)

print(f"✓ Tipo de torneio: {tournament_type.nome}")

# Pegar jogadores
players = Player.objects.filter(
    tournamententry__tournament__season=season,
    tenant=tenant
).distinct().order_by('nome')

if not players.exists():
    print("❌ Nenhum jogador encontrado na temporada!")
    exit(1)

print(f"✓ Jogadores encontrados: {players.count()}")
for p in players[:5]:
    print(f"  - {p.nome}")

# Criar 3 torneios com resultados
tournaments_created = []
base_date = season.data_inicio

for i in range(3):
    tournament_date = base_date + timedelta(days=i*7)
    
    tournament = Tournament.objects.create(
        nome=f"Torneio {season.nome} #{i+1}",
        data=tournament_date,
        buyin=Decimal("100.00"),
        rebuy_valor=Decimal("100.00"),
        addon_valor=Decimal("100.00"),
        rake_tipo="FIXO",
        rake_valor=Decimal("10.00"),
        tipo=tournament_type,
        season=season,
        tenant=tenant,
        total_jogadores=0,
    )
    
    print(f"\n📅 Torneio {i+1} criado: {tournament.nome}")
    tournaments_created.append(tournament)
    
    # Adicionar inscrições para todos os jogadores
    players_list = list(players)
    for idx, player in enumerate(players_list, 1):
        entry = TournamentEntry.objects.create(
            tournament=tournament,
            player=player,
            posicao_entrada=idx,
            confirmado_pelo_admin=True,
            tenant=tenant,
        )
    
    # Lançar resultados (apenas os 5 primeiros recebem prêmio)
    print(f"   Lançando resultados:")
    premios = [
        Decimal("500.00"),  # 1º
        Decimal("300.00"),  # 2º
        Decimal("200.00"),  # 3º
        Decimal("100.00"),  # 4º
        Decimal("50.00"),   # 5º
    ]
    
    for idx, player in enumerate(players_list[:5], 1):
        result = TournamentResult.objects.create(
            tournament=tournament,
            player=player,
            posicao=idx,
            premiacao_recebida=premios[idx-1],
            tenant=tenant,
        )
        print(f"   ✓ {idx}º - {player.nome}: R$ {premios[idx-1]}")
    
    # Atualizar total de jogadores
    tournament.total_jogadores = players_list.count()
    tournament.save()

# Recalcular ranking
print("\n" + "=" * 70)
print("RECALCULANDO RANKING")
print("=" * 70)

from core.views.ranking import _calcular_e_atualizar_stats

for player in players:
    stats = _calcular_e_atualizar_stats(season, player, tenant)
    if stats.pontos_totais > 0:
        print(f"✓ {player.nome}: {stats.pontos_totais} pontos")

print("\n" + "=" * 70)
print("✅ TORNEIOS CRIADOS COM SUCESSO!")
print("=" * 70)
print(f"\nAcesse o ranking em: http://localhost:8000/ranking/{season.id}/")
