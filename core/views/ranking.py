from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, Avg, F, Case, When, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from ..models import (
    Season, Player, Tournament, TournamentEntry, TournamentResult, 
    SeasonInitialPoints, PlayerStatistics, PlayerAchievement
)
from django.utils import timezone
from datetime import timedelta
import json


def _calcular_pontos_resultado(tournament, posicao):
    """
    Calcula pontos para uma posição específica usando o sistema FIXO da temporada.
    """
    if not tournament or posicao is None or posicao < 1:
        return 0
    
    # Usa a tabela fixa da temporada
    if tournament.season.tipo_calculo == "FIXO":
        campo = f"pts_{posicao}lugar"
        if posicao <= 10 and hasattr(tournament.season, campo):
            pontos = getattr(tournament.season, campo, 0)
            return pontos if pontos else 0
        return 1  # Mínimo de 1 ponto
    
    return 0


def _calcular_e_atualizar_stats(season, player):
    """
    Calcula e atualiza as estatísticas consolidadas de um jogador numa temporada.
    """
    # Pontos iniciais
    try:
        pts_iniciais = SeasonInitialPoints.objects.get(season=season, player=player).pontos_iniciais
    except SeasonInitialPoints.DoesNotExist:
        pts_iniciais = 0
    
    # Torneios que o jogador participou
    entradas = TournamentEntry.objects.filter(
        player=player,
        tournament__season=season
    ).select_related('tournament')
    
    total_torneios = entradas.count()
    
    # Resultados
    resultados = TournamentResult.objects.filter(
        player=player,
        tournament__season=season
    ).select_related('tournament')
    
    torneios_com_resultado = resultados.count()
    
    # Contadores
    vitórias = resultados.filter(posicao=1).count()
    top_3 = resultados.filter(posicao__lte=3).count()
    top_5 = resultados.filter(posicao__lte=5).count()
    
    # Financeiro
    total_buyin = Decimal("0")
    for entrada in entradas:
        if entrada.tournament.buyin:
            total_buyin += Decimal(str(entrada.tournament.buyin))
    
    # Prêmios
    total_premio = resultados.aggregate(
        total=Coalesce(Sum('premiacao_recebida'), Decimal("0"))
    )['total'] or Decimal("0")
    
    # ROI
    if total_buyin > 0:
        roi = ((total_premio - total_buyin) / total_buyin) * 100
    else:
        roi = Decimal("0")
    
    # Taxa de ITM (% de torneios com resultado/prêmio)
    if total_torneios > 0:
        taxa_itm = (Decimal(str(torneios_com_resultado)) / Decimal(str(total_torneios))) * 100
    else:
        taxa_itm = Decimal("0")
    
    # Pontos - CALCULA baseado em FIXO
    pontos_resultado = 0
    for resultado in resultados:
        pontos = _calcular_pontos_resultado(resultado.tournament, resultado.posicao)
        pontos_resultado += pontos
    
    pontos_totais = pts_iniciais + pontos_resultado
    
    media_pontos = Decimal("0")
    if torneios_com_resultado > 0:
        media_pontos = Decimal(str(pontos_totais)) / Decimal(str(torneios_com_resultado))
    
    # Salva/atualiza
    stats, created = PlayerStatistics.objects.update_or_create(
        season=season,
        player=player,
        defaults={
            'total_torneios': total_torneios,
            'torneios_com_resultado': torneios_com_resultado,
            'vitórias': vitórias,
            'top_3': top_3,
            'top_5': top_5,
            'total_buyin': total_buyin,
            'total_premio': total_premio,
            'roi': roi,
            'taxa_itm': taxa_itm,
            'pontos_totais': pontos_totais,
            'media_pontos': media_pontos,
        }
    )
    
    return stats


def ranking_avancado(request, season_id):
    """
    Dashboard de Ranking Avançado com:
    - Tabela de ranking com estatísticas
    - Gráficos de evolução
    - Comparações entre jogadores
    - Badges/achievements
    """
    season = get_object_or_404(Season, pk=season_id)
    
    # Atualiza estatísticas de todos os jogadores
    players_season = Player.objects.filter(
        tournamententry__tournament__season=season
    ).distinct()
    
    for player in players_season:
        _calcular_e_atualizar_stats(season, player)
    
    # Ranking ordenado por pontos
    ranking = PlayerStatistics.objects.filter(
        season=season
    ).select_related('player').order_by('-pontos_totais', '-vitórias', '-top_3')
    
    # Adiciona posição
    ranking_with_position = []
    for idx, stat in enumerate(ranking, 1):
        stat.posicao = idx
        ranking_with_position.append(stat)
    
    # Pegador jogador logado (se houver)
    jogador_logado = None
    if request.user.is_authenticated:
        try:
            jogador_logado = Player.objects.get(user=request.user)
        except Player.DoesNotExist:
            pass
    
    # Top 10
    top_10 = ranking_with_position[:10]
    
    # Estatísticas gerais
    total_jogadores = ranking.count()
    total_torneios = Tournament.objects.filter(season=season).count()
    
    # Melhor ROI
    melhor_roi = ranking.filter(roi__gt=0).order_by('-roi').first()
    
    # Maior sequência de ITMs (simples: maior taxa)
    maior_taxa_itm = ranking.filter(taxa_itm__gt=0).order_by('-taxa_itm').first()
    
    # Maior streak de vitórias (mais vitórias)
    maior_vencedor = ranking.filter(vitórias__gt=0).order_by('-vitórias').first()
    
    context = {
        'season': season,
        'ranking': ranking_with_position,
        'top_10': top_10,
        'total_jogadores': total_jogadores,
        'total_torneios': total_torneios,
        'jogador_logado': jogador_logado,
        'melhor_roi': melhor_roi,
        'maior_taxa_itm': maior_taxa_itm,
        'maior_vencedor': maior_vencedor,
    }
    
    return render(request, 'ranking_avancado.html', context)


def estatisticas_jogador(request, season_id, player_id):
    """
    Página detalhada de estatísticas de um jogador.
    """
    season = get_object_or_404(Season, pk=season_id)
    player = get_object_or_404(Player, pk=player_id)
    
    # Atualiza stats
    stats = _calcular_e_atualizar_stats(season, player)
    
    # Histórico de torneios
    resultados = TournamentResult.objects.filter(
        player=player,
        tournament__season=season
    ).select_related('tournament').order_by('-tournament__data')
    
    # Achievements
    achievements = PlayerAchievement.objects.filter(
        season=season,
        player=player
    ).order_by('-obtido_em')
    
    # Comparação com média
    media_pontos_season = PlayerStatistics.objects.filter(
        season=season
    ).aggregate(media=Avg('pontos_totais'))['media'] or 0
    
    variacao = stats.pontos_totais - int(media_pontos_season)
    
    # Gráfico de evolução (por torneio)
    historico = []
    pontos_acumulado = stats.pontos_totais - sum([
        _calcular_pontos_resultado(r.tournament, r.posicao) for r in resultados
    ])
    
    for resultado in reversed(resultados):
        pontos = _calcular_pontos_resultado(resultado.tournament, resultado.posicao)
        pontos_acumulado += pontos
        historico.append({
            'tournament_nome': resultado.tournament.nome,
            'posicao': resultado.posicao,
            'pontos': pontos,
            'premio': float(resultado.premiacao_recebida),
            'acumulado': pontos_acumulado,
        })
    
    context = {
        'season': season,
        'player': player,
        'stats': stats,
        'resultados': resultados,
        'achievements': achievements,
        'media_pontos_season': int(media_pontos_season),
        'variacao': variacao,
        'historico_json': json.dumps(historico),
    }
    
    return render(request, 'estatisticas_jogador.html', context)


def api_ranking_json(request, season_id):
    """
    API que retorna ranking em JSON (para gráficos dinâmicos).
    """
    season = get_object_or_404(Season, pk=season_id)
    
    ranking = PlayerStatistics.objects.filter(
        season=season
    ).select_related('player').order_by('-pontos_totais')[:20]
    
    data = {
        'season': season.nome,
        'jogadores': [
            {
                'nome': stat.player.apelido or stat.player.nome,
                'pontos': stat.pontos_totais,
                'vitórias': stat.vitórias,
                'top_3': stat.top_3,
                'roi': float(stat.roi),
                'taxa_itm': float(stat.taxa_itm),
                'torneios': stat.total_torneios,
            }
            for stat in ranking
        ]
    }
    
    return JsonResponse(data)