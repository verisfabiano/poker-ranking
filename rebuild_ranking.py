#!/usr/bin/env python
"""
Script para recalcular e reconstruir o ranking de todas as temporadas.
Executa: python rebuild_ranking.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Season, Player, PlayerStatistics
from core.views.ranking import _calcular_e_atualizar_stats
from core.views.season import _build_ranking_for_season

print("=" * 60)
print("RECONSTRUINDO RANKING DE TODAS AS TEMPORADAS")
print("=" * 60)

# Pega todas as temporadas ativas
seasons = Season.objects.filter(ativo=True)

if not seasons.exists():
    print("\n⚠️  Nenhuma temporada ativa encontrada!")
    exit(1)

for season in seasons:
    print(f"\n📊 Processando Temporada: {season.nome}")
    print(f"   Período: {season.data_inicio} a {season.data_fim}")
    print(f"   Tipo de Cálculo: {season.tipo_calculo}")
    
    # Pega todos os tenants associados à temporada
    tenants = set()
    from core.models import Tournament, TournamentEntry, TournamentResult
    
    tournaments = Tournament.objects.filter(season=season)
    for t in tournaments:
        if t.tenant:
            tenants.add(t.tenant)
    
    if not tenants:
        tenants.add(None)  # Se não houver tenant específico
    
    for tenant in tenants:
        print(f"\n   🏢 Tenant: {tenant.nome if tenant else 'Padrão'}")
        
        # Pega todos os jogadores que participaram
        players = set()
        entries = TournamentEntry.objects.filter(
            tournament__season=season,
            tournament__tenant=tenant
        )
        for entry in entries:
            players.add(entry.player)
        
        results = TournamentResult.objects.filter(
            tournament__season=season,
            tournament__tenant=tenant
        )
        for result in results:
            players.add(result.player)
        
        print(f"      Atualizando {len(players)} jogadores...")
        
        # Calcula stats para cada jogador
        for player in players:
            stats = _calcular_e_atualizar_stats(season, player, tenant)
            print(f"      ✓ {player.nome} - {stats.pontos_totais} pontos")
        
        # Reconstrói ranking
        print(f"      Reconstruindo ranking geral...")
        ranking = _build_ranking_for_season(season, tenant)
        print(f"      ✓ Ranking reconstruído com {len(ranking)} jogadores")

print("\n" + "=" * 60)
print("✅ RANKING RECALCULADO COM SUCESSO!")
print("=" * 60)
