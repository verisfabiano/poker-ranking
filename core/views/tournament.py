from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import Season, Tournament, TournamentType
from .auth import admin_required

# --- TIPOS DE TORNEIO ---

@admin_required
def tournament_types_list(request):
    tipos = TournamentType.objects.order_by("nome")
    return render(request, "tournament_types_list.html", {"tipos": tipos})

@admin_required
def tournament_type_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        mult = request.POST.get("multiplicador", "1").replace(",", ".")
        try: mult = Decimal(mult)
        except: mult = 1
        
        if nome:
            TournamentType.objects.create(
                nome=nome, 
                multiplicador_pontos=mult,
                usa_regras_padrao=request.POST.get("usa_regras_padrao") == "on"
            )
        return HttpResponseRedirect(reverse("tournament_types_list"))
    return render(request, "tournament_type_form.html", {"tipo": None})

@admin_required
def tournament_type_edit(request, tipo_id):
    tipo = get_object_or_404(TournamentType, id=tipo_id)
    if request.method == "POST":
        tipo.nome = request.POST.get("nome", "")
        # ... lógica de salvamento simplificada ...
        tipo.save()
        return HttpResponseRedirect(reverse("tournament_types_list"))
    return render(request, "tournament_type_form.html", {"tipo": tipo})

# --- TORNEIOS ---

@admin_required
def season_tournaments(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tournaments = Tournament.objects.filter(season=season).order_by("-data")
    return render(request, "tournaments_list.html", {"season": season, "tournaments": tournaments})

@admin_required
def tournament_create(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tipos = TournamentType.objects.order_by("nome")

    if request.method == "POST":
        # Captura de dados
        nome = request.POST.get("nome")
        data_str = request.POST.get("data")
        tipo_id = request.POST.get("tipo_id")
        buy_in_str = request.POST.get("buy_in", "")
        garantido_str = request.POST.get("garantido", "")
        # NOVO CAMPO STACK
        stack_str = request.POST.get("stack_inicial", "10000")

        # Tratamento de valores
        buy_in = Decimal(buy_in_str.replace(",", ".")) if buy_in_str else None
        garantido = Decimal(garantido_str.replace(",", ".")) if garantido_str else None
        
        try: data = datetime.fromisoformat(data_str)
        except: data = datetime.now()

        Tournament.objects.create(
            season=season,
            nome=nome,
            data=data,
            tipo_id=tipo_id,
            buy_in=buy_in,
            garantido=garantido,
            status=request.POST.get("status", "AGENDADO"),
            stack_inicial=int(stack_str) # Salvando stack
        )
        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    return render(request, "tournament_form.html", {"season": season, "tipos": tipos, "tournament": None})

@admin_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    tipos = TournamentType.objects.order_by("nome")

    if request.method == "POST":
        tournament.nome = request.POST.get("nome")
        # ... lógica de update dos campos (buyin, garantido, etc) igual create ...
        stack_str = request.POST.get("stack_inicial", "10000")
        tournament.stack_inicial = int(stack_str)
        
        # Data
        d_str = request.POST.get("data")
        if d_str: tournament.data = datetime.fromisoformat(d_str)
        
        tournament.save()
        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    data_str = tournament.data.strftime("%Y-%m-%dT%H:%M")
    return render(request, "tournament_form.html", {"season": season, "tipos": tipos, "tournament": tournament, "data_str": data_str})