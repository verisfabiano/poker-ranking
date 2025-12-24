#!/usr/bin/env python
"""
Script para debugar por que ranking_avancado está zerado.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Season, PlayerStatistics, Player, Tournament, Tenant

print("=" * 70)
print("DEBUG - Ranking Avançado Zerado")
print("=" * 70)

# Temporada Teste
season = Season.objects.get(nome="Temporada Teste")
tenant = Tenant.objects.get(nome="Veris Poker")

print(f"\n📊 Temporada: {season.nome}")
print(f"🏢 Tenant: {tenant.nome}")

# Verificar PlayerStatistics
stats = PlayerStatistics.objects.filter(season=season, tenant=tenant)
print(f"\n📈 PlayerStatistics registros: {stats.count()}")

if stats.count() > 0:
    print("\n   Amostra:")
    for s in stats[:5]:
        print(f"   - {s.player.nome}: {s.pontos_totais} pts | {s.total_torneios} torneios | {s.vitórias} vitórias")
else:
    print("\n❌ Nenhum registro em PlayerStatistics!")

# Verificar se há jogadores na temporada
players = Player.objects.filter(
    tournamententry__tournament__season=season,
    tenant=tenant
).distinct()

print(f"\n👥 Jogadores na temporada (via TournamentEntry): {players.count()}")
for p in players[:3]:
    print(f"   - {p.nome} (tenant: {p.tenant})")

# Verificar se os dados foram calculados
print(f"\n⚙️ Recalculando stats para todos os jogadores...")
from core.views.ranking import _calcular_e_atualizar_stats

for player in players:
    stats = _calcular_e_atualizar_stats(season, player, tenant)
    print(f"   ✓ {player.nome}: {stats.pontos_totais} pts")

# Verificar novamente
stats_after = PlayerStatistics.objects.filter(season=season, tenant=tenant)
print(f"\n📈 PlayerStatistics após recalcular: {stats_after.count()}")

if stats_after.count() > 0:
    print("\n   Top 3:")
    for s in stats_after.order_by('-pontos_totais')[:3]:
        print(f"   - {s.player.nome}: {s.pontos_totais} pts | ROI: {s.roi}% | ITM: {s.taxa_itm}%")

print("\n" + "=" * 70)
