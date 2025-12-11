from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import Tournament, TournamentEntry, TournamentResult, Player
from .auth import admin_required

@admin_required
def tournament_entries_manage(request, tournament_id):
    # (Mantenha o código desta função igual ao que você já tinha)
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    
    if request.method == "POST":
        if "add_player" in request.POST:
            pid = request.POST.get("novo_player_id")
            if pid:
                p = Player.objects.filter(id=pid).first()
                if p: TournamentEntry.objects.get_or_create(tournament=tournament, player=p)
        
        if "remove_selected" in request.POST:
            ids = request.POST.getlist("remover_entry_id")
            TournamentEntry.objects.filter(tournament=tournament, id__in=ids).delete()
            
        if "save_admin_confirm" in request.POST:
            for entry in tournament.entries.all():
                flag = request.POST.get(f"conf_admin_{entry.id}") is not None
                entry.confirmado_pelo_admin = flag
                entry.save()

        return HttpResponseRedirect(reverse("tournament_entries_manage", args=[tournament.id]) + "?ok=1")

    entries = TournamentEntry.objects.filter(tournament=tournament).select_related("player").order_by("player__nome")
    ids_in = [e.player_id for e in entries]
    disponiveis = Player.objects.filter(ativo=True).exclude(id__in=ids_in).order_by("nome")
    
    return render(request, "tournament_entries.html", {
        "tournament": tournament, "season": season, "entries": entries, "players_disponiveis": disponiveis
    })

@admin_required
def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    
    if request.method == "POST":
        entries = TournamentEntry.objects.filter(tournament=tournament)
        
        for entry in entries:
            pid = entry.player.id
            
            # 1. Atualiza Status de Participação
            entry.participou = request.POST.get(f"participou_{pid}") is not None
            entry.confirmou_presenca = request.POST.get(f"confirmou_{pid}") is not None
            entry.usou_time_chip = request.POST.get(f"timechip_{pid}") is not None
            entry.save()
            
            # 2. Captura Dados de Resultado
            pos_str = request.POST.get(f"pos_{pid}", "").strip()
            ajuste_str = request.POST.get(f"ajuste_{pid}", "").strip()
            prize_str = request.POST.get(f"prize_{pid}", "").replace(",", ".").strip() # NOVO
            
            # Se tem posição OU ajuste OU prêmio, cria/atualiza o resultado
            if pos_str or (ajuste_str and ajuste_str != "0") or (prize_str and prize_str != "0.00"):
                res, _ = TournamentResult.objects.get_or_create(tournament=tournament, player=entry.player)
                
                # Posição
                if pos_str:
                    res.posicao = int(pos_str)
                else:
                    res.posicao = None
                
                # Ajuste Deal
                try: res.pontos_ajuste_deal = int(ajuste_str)
                except: res.pontos_ajuste_deal = 0

                # Premiação (NOVO)
                try: res.premiacao_recebida = Decimal(prize_str) if prize_str else 0
                except: res.premiacao_recebida = 0

                res.save()
            else:
                # Se limpou tudo, remove o resultado
                TournamentResult.objects.filter(tournament=tournament, player=entry.player).delete()
        
        # 3. Recalcula Pontos da Rodada
        tournament.recalcular_pontuacao()
        
        return HttpResponseRedirect(reverse("tournament_results", args=[tournament.id]) + "?ok=1")

    # GET: Monta a lista
    linhas = []
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related("player").order_by("player__nome")
    for e in entries:
        r = TournamentResult.objects.filter(tournament=tournament, player=e.player).first()
        linhas.append({"player": e.player, "entry": e, "result": r})
        
    return render(request, "tournament_results.html", {"tournament": tournament, "season": season, "linhas": linhas})