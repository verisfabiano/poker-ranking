#!/usr/bin/env python
"""
Script para exibir um resumo dos dados populados no sistema.
Mostra temporadas, torneios, jogadores e estatísticas.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Season, Tournament, Player, TournamentResult, PlayerStatistics, Tenant
from django.db.models import Sum, Count

def exibir_resumo():
    """Exibe um resumo dos dados populados"""
    
    # Obter tenant de teste
    tenant = Tenant.objects.filter(slug='clube-teste').first()
    
    if not tenant:
        print("❌ Tenant 'Clube Poker Teste' não encontrado!")
        return
    
    print("\n" + "="*70)
    print(f"  RESUMO DOS DADOS POPULADOS - {tenant.nome.upper()}")
    print("="*70 + "\n")
    
    # Listar temporadas
    temporadas = Season.objects.filter(tenant=tenant).order_by('-data_inicio')
    print(f"📊 TEMPORADAS ({temporadas.count()}):")
    print("-" * 70)
    
    for season in temporadas:
        num_torneios = Tournament.objects.filter(season=season).count()
        num_resultados = TournamentResult.objects.filter(tournament__season=season).count()
        num_jogadores = Player.objects.filter(
            tournamentresult__tournament__season=season
        ).distinct().count()
        
        print(f"  • {season.nome}")
        print(f"    Período: {season.data_inicio.strftime('%d/%m/%Y')} a {season.data_fim.strftime('%d/%m/%Y')}")
        print(f"    Tipo de cálculo: {season.get_tipo_calculo_display()}")
        print(f"    Torneios: {num_torneios} | Jogadores: {num_jogadores} | Resultados: {num_resultados}")
        print()
    
    # Listar torneios
    print(f"\n🎰 TORNEIOS ({Tournament.objects.filter(tenant=tenant).count()}):")
    print("-" * 70)
    
    for season in temporadas:
        print(f"\n  {season.nome}:")
        torneios = Tournament.objects.filter(season=season).order_by('-data')
        
        for torneio in torneios:
            num_inscritos = torneio.tournamententry_set.count()
            num_resultados = TournamentResult.objects.filter(tournament=torneio).count()
            premiacao_total = TournamentResult.objects.filter(
                tournament=torneio
            ).aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or 0
            
            print(f"    • {torneio.nome}")
            print(f"      Data: {torneio.data.strftime('%d/%m/%Y %H:%M')} | "
                  f"Buy-in: R${torneio.buyin:.2f} | "
                  f"Inscritos: {num_inscritos} | "
                  f"Resultados: {num_resultados} | "
                  f"Prêmios: R${premiacao_total:.2f}")
    
    # Listar Top 10 jogadores por temporada
    print(f"\n\n🏆 TOP 10 JOGADORES POR TEMPORADA:")
    print("-" * 70)
    
    for season in temporadas:
        print(f"\n  {season.nome}:")
        stats = PlayerStatistics.objects.filter(
            season=season, 
            tenant=tenant
        ).select_related('player').order_by('-pontos_totais')[:10]
        
        if not stats:
            print("    Sem dados de estatísticas ainda.")
            continue
        
        for idx, stat in enumerate(stats, 1):
            print(f"    {idx:2d}. {stat.player.apelido or stat.player.nome:20s} "
                  f"| {stat.pontos_totais:3d} pts "
                  f"| {stat.total_torneios} torneios "
                  f"| {stat.vitórias} vitórias "
                  f"| ROI: {stat.roi:6.1f}% "
                  f"| ITM: {stat.taxa_itm:5.1f}%")
    
    # Estatísticas gerais
    print(f"\n\n📈 ESTATÍSTICAS GERAIS:")
    print("-" * 70)
    
    total_resultados = TournamentResult.objects.filter(tournament__tenant=tenant).count()
    total_jogadores = Player.objects.filter(tenant=tenant).count()
    total_torneios = Tournament.objects.filter(tenant=tenant).count()
    total_premiacao = TournamentResult.objects.filter(
        tournament__tenant=tenant
    ).aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or 0
    
    print(f"  • Total de jogadores: {total_jogadores}")
    print(f"  • Total de torneios: {total_torneios}")
    print(f"  • Total de resultados: {total_resultados}")
    print(f"  • Total de prêmios distribuídos: R${total_premiacao:.2f}")
    
    print("\n" + "="*70)
    print("  ✅ Dados prontos para testes!")
    print("="*70)
    print("\n📱 URLs úteis:")
    print("  • Ranking Geral: http://localhost:8000/ranking/")
    print("  • Ranking por Temporada: http://localhost:8000/ranking/<id>/")
    print("  • Ranking Avançado: http://localhost:8000/ranking/<id>/avancado/")
    print("  • Dashboard Financeiro: http://localhost:8000/financeiro/dashboard/")
    print("  • Detalhes Torneio: http://localhost:8000/torneio/<id>/financeiro/")
    print()

if __name__ == '__main__':
    exibir_resumo()
