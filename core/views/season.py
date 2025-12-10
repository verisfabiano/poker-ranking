from datetime import date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from ..models import Season, TournamentResult, TournamentEntry, SeasonInitialPoints, Player
from .auth import admin_required # Importando o decorator do arquivo vizinho

# --- LÓGICA DE RANKING ---

def _build_ranking_for_season(season):
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

# --- VIEWS PÚBLICAS ---

def ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    return render(request, "ranking.html", {"season": season, "ranking": _build_ranking_for_season(season)})

def tv_ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    return render(request, "tv_ranking.html", {"season": season, "ranking": _build_ranking_for_season(season)})

# --- ADMIN VIEWS ---

@admin_required
def painel_home(request):
    seasons = Season.objects.order_by("-data_inicio")
    return render(request, "painel_home.html", {"seasons": seasons})

@admin_required
def seasons_list(request):
    seasons = Season.objects.order_by("-data_inicio")
    return render(request, "seasons_list.html", {"seasons": seasons})

@admin_required
def season_create(request):
    if request.method == "POST":
        # ... lógica de criação ...
        nome = request.POST.get("nome", "").strip()
        data_inicio = request.POST.get("data_inicio", "")
        data_fim = request.POST.get("data_fim", "")
        ativo = request.POST.get("ativo") == "on"
        
        try:
            d_ini = date.fromisoformat(data_inicio)
            d_fim = date.fromisoformat(data_fim)
        except ValueError:
            d_ini = date.today()
            d_fim = date.today()

        if nome:
            Season.objects.create(nome=nome, data_inicio=d_ini, data_fim=d_fim, ativo=ativo)
        return HttpResponseRedirect(reverse("seasons_list"))
    return render(request, "season_form.html", {"season": None})

@admin_required
def season_edit(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    if request.method == "POST":
        season.nome = request.POST.get("nome", "").strip()
        # ... resto da lógica de update ...
        season.ativo = request.POST.get("ativo") == "on"
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

    return render(request, "season_initial_points.html", {"season": season, "linhas": linhas, "mensagem": mensagem})