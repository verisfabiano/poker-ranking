from datetime import date
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from ..models import Season, TournamentResult, TournamentEntry, SeasonInitialPoints, Player, Tournament
from ..decorators.tenant_decorators import admin_required
from .ranking import tenant_required


# ============================================================
#  FUNÇÕES HELPER DE CÁLCULO
# ============================================================

def calcular_pontos_posicao(posicao, total_jogadores, buyin_valor, multiplicador_tipo=None, tabela_fixa=None):
    """
    Calcula pontos baseado no sistema escolhido.
    
    Sistema com duas opções:
    1. FIXO: Usa tabela pré-definida + multiplicador do tipo de torneio
    2. DINÂMICO: Uso automático baseado em buy-in e número de participantes
    
    Com expansão dinâmica de posições: quanto maior o torneio, mais posições pontuam.
    
    Args:
        posicao: Posição final (1, 2, 3, etc)
        total_jogadores: Total de jogadores no torneio
        buyin_valor: Valor do buy-in em reais
        multiplicador_tipo: Multiplicador do tipo (usado apenas com tabela_fixa para modo FIXO)
        tabela_fixa: Dicionário com tabela de pontos {1: 14, 2: 11, ...}
    
    Returns:
        Pontos calculados (inteiro)
    """
    
    if posicao is None or posicao < 1 or total_jogadores < 1:
        return 0
    
    if posicao > total_jogadores:
        return 0
    
    # Se tabela_fixa fornecida, usa sistema fixo com multiplicador
    if tabela_fixa:
        pts = tabela_fixa.get(posicao, 0)
        if pts > 0 and multiplicador_tipo:
            pts = int(pts * Decimal(str(multiplicador_tipo)))
        return pts
    
    # Sistema dinâmico com EXPANSÃO DE POSIÇÕES
    # Quanto mais jogadores, mais posições recebem pontos
    
    # Tabela base (sempre disponível)
    tabela_base = {
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
    
    # Expandir tabela dinamicamente baseado no número de participantes
    # Proporciona ~10-15% das posições do torneio para pontuar
    tabela_expandida = tabela_base.copy()
    
    # Calcular quantas posições devem pontuar baseado no tamanho do torneio
    proporcao_posicoes = Decimal(str(total_jogadores)) / Decimal("100")  # 1% por 100 jogadores
    max_posicoes = max(
        10,  # Mínimo 10 posições
        min(
            int(Decimal(str(total_jogadores)) * Decimal("0.15")),  # Máximo 15% das posições
            30  # Nunca mais que 30 posições
        )
    )
    
    # Adicionar posições 11+ com valores progressivamente menores
    if max_posicoes > 10:
        for pos in range(11, max_posicoes + 1):
            # Decrescimento: começa em 4 e vai diminuindo
            valor = max(Decimal("1"), Decimal("5") - (Decimal(pos - 10) * Decimal("0.3")))
            tabela_expandida[pos] = valor
    
    # Verificar se a posição está na tabela
    if posicao not in tabela_expandida:
        # Se ultrapassar as posições pontuadas, retorna 0
        return 0
    
    mult_posicao = tabela_expandida[posicao]
    # O sistema dinâmico é inteligente: buy-in alto = mais pontos naturalmente
    pontos_base = (Decimal(total_jogadores) * Decimal(buyin_valor) / Decimal("100"))
    pontos_finais = pontos_base * mult_posicao / Decimal("100")
    
    return int(pontos_finais.to_integral_value(rounding='ROUND_UP'))


def _build_ranking_for_season(season, tenant=None):
    """
    Constrói ranking para uma temporada.
    Calcula pontos baseado nas posições dos resultados.
    """
    # Filtro base - sempre filtrar por season
    # Tenant é opcional, pois pode haver resultados sem tenant preenchido
    
    # Pontos iniciais
    init_filter = {"season": season}
    if tenant:
        init_filter["tenant"] = tenant
    
    iniciais_dict = {}
    for init_record in SeasonInitialPoints.objects.filter(**init_filter):
        iniciais_dict[init_record.player_id] = init_record.pontos_iniciais
    
    ranking_dict = {}
    
    # Helper para popular dict
    def get_or_create_p(pid, nome, apelido):
        if pid not in ranking_dict:
            ranking_dict[pid] = {
                "nome": apelido or nome,
                "pontos_resultado": 0,
                "pontos_iniciais": iniciais_dict.get(pid, 0),
            }
        return ranking_dict[pid]
    
    # Processar resultados e calcular pontos por posição
    from .ranking import _calcular_pontos_resultado
    
    # Filtro por season - obrigatório. Tenant é opcional
    resultados = TournamentResult.objects.filter(
        tournament__season=season
    ).select_related('tournament', 'player')
    
    # Se tenant especificado, filtrar também por tenant
    # Mas considerar resultados sem tenant (null)
    if tenant:
        resultados = resultados.filter(
            tournament__tenant=tenant
        )
    
    for resultado in resultados:
        if resultado.posicao and resultado.posicao > 0:
            pontos = _calcular_pontos_resultado(resultado.tournament, resultado.posicao)
            p = get_or_create_p(resultado.player_id, resultado.player.nome, resultado.player.apelido)
            p["pontos_resultado"] += pontos
    
    # Builds lista de ranking
    ranking_lista = []
    for pid, dados in ranking_dict.items():
        total = dados["pontos_resultado"] + dados["pontos_iniciais"]
        ranking_lista.append({
            "player_id": pid,
            "nome": dados["nome"],
            "pontos": total,
            "pontos_resultado": dados["pontos_resultado"],
            "pontos_iniciais": dados["pontos_iniciais"],
        })
    
    # Ordena por pontos totais
    ranking_lista.sort(key=lambda x: (-(x["pontos"]), -(x["pontos_resultado"]), -(x["pontos_iniciais"]), x["nome"].lower()))
    
    # Adiciona posições
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

@login_required
def ranking_season(request, season_id):
    """
    Renderiza o ranking unificado da temporada com todas as funcionalidades.
    Aplica filtro para mostrar apenas jogadores com pontos > 0.
    """
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    
    from .ranking import _calcular_e_atualizar_stats
    from core.models import PlayerStatistics
    
    # Atualiza stats de todos os jogadores
    players_season = Player.objects.filter(
        tournamententry__tournament__season=season,
        tenant=request.tenant
    ).distinct()
    
    for player in players_season:
        _calcular_e_atualizar_stats(season, player, request.tenant)
    
    # Ranking ordenado por pontos - EXCLUINDO JOGADORES SEM PONTUAÇÃO
    ranking = PlayerStatistics.objects.filter(
        season=season,
        tenant=request.tenant,
        pontos_totais__gt=0  # 👈 Filtro: apenas jogadores com pontos > 0
    ).select_related('player').order_by('-pontos_totais', '-vitórias', '-top_3')
    
    ranking_with_position = []
    minha_posicao = None
    minha_stats = None
    
    for idx, stat in enumerate(ranking, 1):
        stat.posicao = idx
        ranking_with_position.append(stat)
        
        # Se é o jogador logado
        if request.user.is_authenticated and request.user == stat.player.user:
            minha_posicao = idx
            minha_stats = stat
    
    # Estatísticas gerais
    total_jogadores = ranking.count()
    total_torneios = Tournament.objects.filter(season=season, tenant=request.tenant).count()
    
    # Melhor ROI
    melhor_roi = ranking.filter(roi__gt=0).order_by('-roi').first()
    
    # Maior vencedor
    maior_vencedor = ranking.filter(vitórias__gt=0).order_by('-vitórias').first()
    
    context = {
        'season': season,
        'ranking': ranking_with_position,
        'total_jogadores': total_jogadores,
        'total_torneios': total_torneios,
        'jogador_logado': request.user if request.user.is_authenticated else None,
        'minha_posicao': minha_posicao,
        'minha_stats': minha_stats,
        'melhor_roi': melhor_roi,
        'maior_vencedor': maior_vencedor,
    }
    
    return render(request, 'ranking_unified.html', context)


@login_required
def tv_ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    return render(request, "tv_ranking.html", {"season": season, "ranking": _build_ranking_for_season(season, request.tenant)})


@login_required
def painel_home(request):
    """Dashboard principal do sistema"""
    # Garante que o usuário tem acesso a um tenant
    if not hasattr(request, 'tenant') or not request.tenant:
        # Tentar obter o primeiro tenant do usuário
        from ..models import TenantUser
        tenant_user = TenantUser.objects.select_related('tenant').filter(
            user=request.user,
            tenant__ativo=True
        ).first()
        
        if tenant_user:
            request.tenant = tenant_user.tenant
        else:
            # Redireccionar para uma página de erro ou home
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('player_home'))
    
    seasons = Season.objects.filter(tenant=request.tenant).order_by("-data_inicio")
    
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
    seasons = Season.objects.filter(tenant=request.tenant).order_by("-data_inicio")
    
    # Calcula ranking para cada temporada
    for season in seasons:
        season.ranking = _build_ranking_for_season(season, request.tenant)
    
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
                    tenant=request.tenant,
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
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    
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
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    mensagem = None
    players = Player.objects.filter(ativo=True, tenant=request.tenant).order_by("nome")

    if request.method == "POST":
        for player in players:
            val = request.POST.get(f"pontos_{player.id}", "").strip()
            if val == "":
                SeasonInitialPoints.objects.filter(season=season, player=player, tenant=request.tenant).delete()
            else:
                pts = int(val) if val.isdigit() else 0
                SeasonInitialPoints.objects.update_or_create(
                    season=season, player=player, tenant=request.tenant, defaults={"pontos_iniciais": pts}
                )
        mensagem = "Salvo com sucesso."

    iniciais_map = {sip.player_id: sip.pontos_iniciais for sip in SeasonInitialPoints.objects.filter(season=season, tenant=request.tenant)}
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
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    player = get_object_or_404(Player, id=player_id, tenant=request.tenant)
    
    resultados = TournamentResult.objects.filter(
        player=player, tournament__season=season, tenant=request.tenant
    ).order_by("tournament__data")
    
    return render(
        request,
        "player_progress.html",
        {"season": season, "player": player, "resultados": resultados},
    )


from django.http import JsonResponse

@admin_required
def api_seasons(request):
    """API para listar temporadas do tenant"""
    seasons = Season.objects.filter(tenant=request.tenant).values('id', 'nome', 'data_inicio', 'data_fim').order_by('-data_inicio')
    
    return JsonResponse({
        'seasons': list(seasons)
    })