#!/usr/bin/env python
"""
Script para exibir dados do Veris Poker
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Season, Tenant, Tournament, Player, TournamentResult, PlayerStatistics

veris = Tenant.objects.filter(slug='veris-poker').first()

print('\n╔════════════════════════════════════════════════════════════╗')
print('║          DADOS POPULADOS - VERIS POKER                    ║')
print('╚════════════════════════════════════════════════════════════╝\n')

# Resumo geral
print('📊 RESUMO GERAL:')
print(f'  • Tenant: {veris.nome} (ID: {veris.id})')
print(f'  • Jogadores: {Player.objects.filter(tenant=veris).count()}')
print(f'  • Temporadas: {Season.objects.filter(tenant=veris, nome__contains="Temporada").count()}')
print(f'  • Torneios: {Tournament.objects.filter(tenant=veris).count()}')
print(f'  • Resultados: {TournamentResult.objects.filter(tournament__tenant=veris).count()}')
print()

# Temporadas
temporadas = Season.objects.filter(tenant=veris, nome__contains='Temporada').order_by('-data_inicio')
print('🏆 TOP 5 POR TEMPORADA:\n')
for s in temporadas:
    stats = PlayerStatistics.objects.filter(season=s, tenant=veris).order_by('-pontos_totais')[:5]
    print(f'  {s.nome} (ID: {s.id}):')
    if stats:
        for idx, stat in enumerate(stats, 1):
            print(f'    {idx}. {stat.player.apelido or stat.player.nome:20s} | {stat.pontos_totais:3d} pts | {stat.total_torneios} torneios')
    print()

print('\n📱 URLS DO VERIS POKER:\n')
for s in temporadas:
    print(f'  • Ranking {s.nome}:     http://localhost:8000/ranking/{s.id}/')
    print(f'  • Avançado {s.nome}:    http://localhost:8000/ranking/{s.id}/avancado/')
    print()

print('💰 FINANCEIRO:')
print('  • Dashboard Financeiro: http://localhost:8000/financeiro/dashboard/')
print()
