from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Player, Tournament, TournamentEntry, TournamentResult, SeasonInitialPoints, Season
from .auth import admin_required

# --- ADMIN CRUD ---

@admin_required
def players_list(request):
    players = Player.objects.order_by("nome")
    return render(request, "players_list.html", {"players": players})

@admin_required
def player_create(request):
    if request.method == "POST":
        Player.objects.create(
            nome=request.POST.get("nome"),
            apelido=request.POST.get("apelido"),
            cpf=request.POST.get("cpf"),
            telefone=request.POST.get("telefone"),
            ativo=request.POST.get("ativo") == "on"
        )
        return HttpResponseRedirect(reverse("players_list"))
    return render(request, "player_form.html", {"player": None})

@admin_required
def player_edit(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == "POST":
        player.nome = request.POST.get("nome")
        # ... update ...
        player.ativo = request.POST.get("ativo") == "on"
        player.save()
        return HttpResponseRedirect(reverse("players_list"))
    return render(request, "player_form.html", {"player": player})

# --- PORTAL DO JOGADOR ---

@login_required
def player_tournaments(request):
    player = get_object_or_404(Player, user=request.user)
    torneios = Tournament.objects.filter(status="AGENDADO").order_by("data")
    
    lista = []
    for t in torneios:
        entry = TournamentEntry.objects.filter(tournament=t, player=player).first()
        lista.append({
            "torneio": t,
            "inscrito": bool(entry),
            "confirmado": entry.confirmado_pelo_admin if entry else False
        })
    return render(request, "player_tournaments.html", {"torneios": lista})

@login_required
def confirm_presence(request, tournament_id):
    player = get_object_or_404(Player, user=request.user)
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    if tournament.status == "AGENDADO":
        entry = TournamentEntry.objects.filter(tournament=tournament, player=player).first()
        if entry:
            entry.delete() # Cancela
        else:
            TournamentEntry.objects.create(tournament=tournament, player=player, confirmou_presenca=True)
            
    return HttpResponseRedirect(reverse("player_tournaments"))

def player_progress_season(request, season_id, player_id):
    season = get_object_or_404(Season, id=season_id)
    player = get_object_or_404(Player, id=player_id)
    
    # Pontos iniciais
    sip = SeasonInitialPoints.objects.filter(season=season, player=player).first()
    pontos_iniciais = sip.pontos_iniciais if sip else 0
    
    progresso = []
    acumulado = pontos_iniciais
    
    # Se há pontos iniciais, registra como ajuste (não como evento principal)
    if pontos_iniciais > 0:
        progresso.append({
            "tipo": "iniciais",
            "descricao": "Ajuste de pontos iniciais",
            "data": None,
            "posicao": None,
            "pontos_rodada": pontos_iniciais,
            "acumulado": acumulado,
        })
    
    # Torneios em ordem cronológica
    torneios = Tournament.objects.filter(season=season).order_by("data")
    for t in torneios:
        result = TournamentResult.objects.filter(tournament=t, player=player).first()
        pts = result.pontos_finais if result else 0
        posicao = result.posicao if result else None
        
        acumulado += pts
        progresso.append({
            "tipo": "torneio",
            "descricao": t.nome,
            "data": t.data,
            "torneio": t,
            "posicao": posicao,
            "pontos_rodada": pts,
            "acumulado": acumulado,
        })
    
    return render(
        request,
        "player_progress.html",
        {
            "season": season,
            "player": player,
            "progresso": progresso,
            "pontos_iniciais": pontos_iniciais,
            "total_final": acumulado,
        },
    )