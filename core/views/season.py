from datetime import date
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from ..models import Season, TournamentResult, TournamentEntry, SeasonInitialPoints, Player, Tournament
from .auth import admin_required


# ============================================================
#  FUNÇÕES HELPER DE CÁLCULO
# ============================================================

def calcular_pontos_posicao(posicao, total_jogadores, buyin_valor, multiplicador_tipo, tabela_fixa=None):
    """
    Calcula pontos baseado no sistema escolhido.
    
    Args:
        posicao: Posição final (1, 2, 3, etc)
        total_jogadores: Total de jogadores no torneio
        buyin_valor: Valor do buy-in em reais
        multiplicador_tipo: Multiplicador do tipo de torneio
        tabela_fixa: Dicionário com tabela de pontos {1: 14, 2: 11, ...}
    
    Returns:
        Pontos calculados (inteiro)
    """
    
    if posicao is None or posicao < 1 or total_jogadores < 1:
        return 0
    
    if posicao > total_jogadores:
        return 0
    
    # Se tabela_fixa fornecida, usa sistema fixo
    if tabela_fixa:
        return tabela_fixa.get(posicao, 1)
    
    # Sistema dinâmico
    tabela_posicoes = {
        1: Decimal("100"),
        2: Decimal("70"),
        3: Decimal("50"),
        4: Decimal("35"),
        5: Decimal("25"),
        6: Decimal("20"),
        7: Decimal("15"),
        8: Decimal("12"),
        9: Decimal("8"),
        10: Decimal("5"),
    }
    
    mult_posicao = tabela_posicoes.get(posicao, Decimal("1"))
    pontos_base = (Decimal(total_jogadores) * Decimal(buyin_valor) / Decimal("100")) * Decimal(multiplicador_tipo)
    pontos_finais = pontos_base * mult_posicao / Decimal("100")
    
    return int(pontos_finais.to_integral_value(rounding='ROUND_UP'))


def _build_ranking_for_season(season):
    """
    Constrói ranking para uma temporada.
    Agora usa o sistema de cálculo configurado na temporada.
    """
    resultados = (
        TournamentResult.objects.filter(tournament__season=season)
        .values("player__id", "player__nome", "player__apelido")
        .annotate(total_resultado=Sum("pontos_finais"))
    )
    participacoes = (
        TournamentEntry.objects.filter(tournament__season=season)
        .values("player__id")
        .annotate(total_participacao=Sum("pontos_participacao"))
    )
    iniciais = (
        SeasonInitialPoints.objects.filter(season=season)
        .values("player__id", "player__nome", "player__apelido")
        .annotate(total_iniciais=Sum("pontos_iniciais"))
    )

    ranking_dict = {}

    # Helper interno para popular dict
    def get_or_create_p(pid, nome):
        if pid not in ranking_dict:
            ranking_dict[pid] = {
                "nome": nome, "pontos_resultado": 0,
                "pontos_participacao": 0, "pontos_iniciais": 0
            }
        return ranking_dict[pid]

    for r in resultados:
        p = get_or_create_p(r["player__id"], r["player__apelido"] or r["player__nome"])
        p["pontos_resultado"] = r["total_resultado"] or 0

    for p_entry in participacoes:
        p = get_or_create_p(p_entry["player__id"], "Desconhecido")
        p["pontos_participacao"] = p_entry["total_participacao"] or 0

    for i in iniciais:
        p = get_or_create_p(i["player__id"], i["player__apelido"] or i["player__nome"])
        p["pontos_iniciais"] = i["total_iniciais"] or 0

    ranking_lista = []
    for pid, dados in ranking_dict.items():
        total = dados["pontos_resultado"] + dados["pontos_participacao"] + dados["pontos_iniciais"]
        ranking_lista.append({
            "player_id": pid, "nome": dados["nome"], "pontos": total,
            "pontos_resultado": dados["pontos_resultado"],
            "pontos_participacao": dados["pontos_participacao"],
            "pontos_iniciais": dados["pontos_iniciais"],
        })

    ranking_lista.sort(key=lambda x: (-(x["pontos"]), -(x["pontos_resultado"]), -(x["pontos_iniciais"]), x["nome"].lower()))

    # Rank positions
    last_pontos = None
    last_rank = 0
    index = 0
    pontos_count = {}
    for item in ranking_lista:
        pontos_count[item["pontos"]] = pontos_count.get(item["pontos"], 0) + 1

    for item in ranking_lista:
        index += 1
        if last_pontos is None or item["pontos"] < last_pontos:
            rank = index
        else:
            rank = last_rank
        item["posicao"] = rank
        item["empatado"] = pontos_count[item["pontos"]] > 1
        last_pontos = item["pontos"]
        last_rank = rank

    return ranking_lista


# ============================================================
#  VIEWS PÚBLICAS
# ============================================================

def ranking_season(request, season_id):
    """
    Renderiza o ranking da temporada.
    Se jogador logado: mostra view simplificada (ranking_jogador.html)
    Se admin: mostra view completa (ranking.html)
    """
    season = get_object_or_404(Season, id=season_id)
    
    # Se for jogador logado, renderiza view simplificada
    if request.user.is_authenticated and not request.user.is_staff:
        from .ranking import _calcular_e_atualizar_stats
        from core.models import PlayerStatistics
        
        # Atualiza stats de todos os jogadores
        players_season = Player.objects.filter(
            tournamententry__tournament__season=season
        ).distinct()
        
        for player in players_season:
            _calcular_e_atualizar_stats(season, player)
        
        # Ranking ordenado por pontos
        ranking = PlayerStatistics.objects.filter(
            season=season
        ).select_related('player').order_by('-pontos_totais', '-vitórias', '-top_3')
        
        ranking_with_position = []
        minha_posicao = None
        minha_stats = None
        
        for idx, stat in enumerate(ranking, 1):
            stat.posicao = idx
            ranking_with_position.append(stat)
            
            # Se é o jogador logado
            if request.user == stat.player.user:
                minha_posicao = idx
                minha_stats = stat
        
        context = {
            'season': season,
            'ranking': ranking_with_position,
            'total_jogadores': ranking.count(),
            'total_torneios': Tournament.objects.filter(season=season).count(),
            'jogador_logado': request.user,
            'minha_posicao': minha_posicao,
            'minha_stats': minha_stats,
        }
        
        return render(request, 'ranking_jogador.html', context)
    
    # Admin vê ranking tradicional
    return render(request, "ranking.html", {"season": season, "ranking": _build_ranking_for_season(season)})


def tv_ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    return render(request, "tv_ranking.html", {"season": season, "ranking": _build_ranking_for_season(season)})


def painel_home(request):
    """Dashboard principal do sistema"""
    seasons = Season.objects.order_by("-data_inicio")
    
    return render(
        request,
        "painel_home.html",
        {
            "seasons": seasons,
        },
    )


# ============================================================
#  ADMIN VIEWS
# ============================================================

@admin_required
def seasons_list(request):
    seasons = Season.objects.order_by("-data_inicio")
    
    # Calcula ranking para cada temporada
    for season in seasons:
        season.ranking = _build_ranking_for_season(season)
    
    return render(request, "seasons_list.html", {"seasons": seasons})


@admin_required
def season_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_inicio_str = request.POST.get("data_inicio", "").strip()
        data_fim_str = request.POST.get("data_fim", "").strip()
        ativo = request.POST.get("ativo") == "on"
        tipo_calculo = request.POST.get("tipo_calculo", "FIXO")
        
        try:
            data_inicio = date.fromisoformat(data_inicio_str) if data_inicio_str else None
            data_fim = date.fromisoformat(data_fim_str) if data_fim_str else None
            
            if data_inicio and data_fim:
                season = Season.objects.create(
                    nome=nome,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    ativo=ativo,
                    tipo_calculo=tipo_calculo,
                )
                
                # Se FIXO, salva os pontos
                if tipo_calculo == "FIXO":
                    for pos in range(1, 11):
                        pts_field = f"pts_{pos}lugar"
                        pts_value = request.POST.get(pts_field, "0")
                        try:
                            pts_int = int(pts_value)
                            setattr(season, pts_field, pts_int)
                        except ValueError:
                            pass
                    season.save()
                
                return HttpResponseRedirect(reverse("seasons_list"))
        except (ValueError, TypeError):
            pass
    
    return render(request, "season_form.html", {"season": None})


@admin_required
def season_edit(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    
    if request.method == "POST":
        season.nome = request.POST.get("nome", "").strip()
        season.tipo_calculo = request.POST.get("tipo_calculo", "FIXO")
        season.ativo = request.POST.get("ativo") == "on"
        
        try:
            data_inicio_str = request.POST.get("data_inicio", "").strip()
            data_fim_str = request.POST.get("data_fim", "").strip()
            
            if data_inicio_str:
                season.data_inicio = date.fromisoformat(data_inicio_str)
            if data_fim_str:
                season.data_fim = date.fromisoformat(data_fim_str)
        except (ValueError, TypeError):
            pass
        
        # Se FIXO, atualiza pontos
        if season.tipo_calculo == "FIXO":
            for pos in range(1, 11):
                pts_field = f"pts_{pos}lugar"
                pts_value = request.POST.get(pts_field, "0")
                try:
                    setattr(season, pts_field, int(pts_value))
                except ValueError:
                    pass
        
        season.save()
        return HttpResponseRedirect(reverse("seasons_list"))
    
    return render(request, "season_form.html", {"season": season})


@admin_required
def season_initial_points(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    mensagem = None
    players = Player.objects.filter(ativo=True).order_by("nome")

    if request.method == "POST":
        for player in players:
            val = request.POST.get(f"pontos_{player.id}", "").strip()
            if val == "":
                SeasonInitialPoints.objects.filter(season=season, player=player).delete()
            else:
                pts = int(val) if val.isdigit() else 0
                SeasonInitialPoints.objects.update_or_create(
                    season=season, player=player, defaults={"pontos_iniciais": pts}
                )
        mensagem = "Salvo com sucesso."

    iniciais_map = {sip.player_id: sip.pontos_iniciais for sip in SeasonInitialPoints.objects.filter(season=season)}
    linhas = [{"player": p, "pontos": iniciais_map.get(p.id, 0)} for p in players]
    
    return render(
        request,
        "season_initial_points.html",
        {
            "season": season,
            "linhas": linhas,
            "mensagem": mensagem,
        },
    )


def player_progress_season(request, season_id, player_id):
    season = get_object_or_404(Season, id=season_id)
    player = get_object_or_404(Player, id=player_id)
    
    resultados = TournamentResult.objects.filter(
        player=player, tournament__season=season
    ).order_by("tournament__data")
    
    return render(
        request,
        "player_progress.html",
        {"season": season, "player": player, "resultados": resultados},
    )