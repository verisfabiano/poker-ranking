from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import Season, Tournament, TournamentType
from .auth import admin_required

# --- HELPER PARA MOEDA ---
def _get_decimal(request, field_name):
    """
    Tenta converter o valor do POST para Decimal.
    Aceita vírgula ou ponto como separador. Retorna 0.00 se vazio ou inválido.
    """
    val = request.POST.get(field_name, "").replace(",", ".").strip()
    if not val:
        return Decimal("0.00")
    try:
        return Decimal(val)
    except (ValueError, InvalidOperation):
        return Decimal("0.00")

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
        # Lógica simplificada de salvamento do tipo
        mult = request.POST.get("multiplicador", "1").replace(",", ".")
        try: tipo.multiplicador_pontos = Decimal(mult)
        except: pass
        
        tipo.usa_regras_padrao = request.POST.get("usa_regras_padrao") == "on"
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
        # 1. Dados Básicos
        nome = request.POST.get("nome")
        tipo_id = request.POST.get("tipo_id")
        data_str = request.POST.get("data")
        status = request.POST.get("status", "AGENDADO")
        
        try: data = datetime.fromisoformat(data_str)
        except: data = datetime.now()

        # 2. Dados Financeiros e Estrutura (Convertidos via Helper)
        buy_in = _get_decimal(request, "buy_in")
        rake = _get_decimal(request, "rake")
        garantido = _get_decimal(request, "garantido")
        rebuy_cost = _get_decimal(request, "rebuy_cost")
        addon_cost = _get_decimal(request, "addon_cost")
        time_chip_cost = _get_decimal(request, "time_chip_cost")
        
        stack_str = request.POST.get("stack_inicial", "10000")
        
        # 3. Criação
        Tournament.objects.create(
            season=season,
            nome=nome,
            data=data,
            tipo_id=tipo_id,
            status=status,
            # Campos Financeiros
            buy_in=buy_in,
            rake=rake,
            garantido=garantido,
            rebuy_cost=rebuy_cost,
            addon_cost=addon_cost,
            time_chip_cost=time_chip_cost,
            # Estrutura
            stack_inicial=int(stack_str) if stack_str.isdigit() else 10000
        )
        
        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    return render(request, "tournament_form.html", {"season": season, "tipos": tipos, "tournament": None})

@admin_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    tipos = TournamentType.objects.order_by("nome")

    if request.method == "POST":
        # 1. Atualiza Dados Básicos
        tournament.nome = request.POST.get("nome")
        tournament.tipo_id = request.POST.get("tipo_id")
        tournament.status = request.POST.get("status")

        d_str = request.POST.get("data")
        if d_str: 
            try: tournament.data = datetime.fromisoformat(d_str)
            except: pass

        # 2. Atualiza Dados Financeiros
        tournament.buy_in = _get_decimal(request, "buy_in")
        tournament.rake = _get_decimal(request, "rake")
        tournament.garantido = _get_decimal(request, "garantido")
        tournament.rebuy_cost = _get_decimal(request, "rebuy_cost")
        tournament.addon_cost = _get_decimal(request, "addon_cost")
        tournament.time_chip_cost = _get_decimal(request, "time_chip_cost")

        # 3. Atualiza Estrutura
        stack_str = request.POST.get("stack_inicial", "10000")
        tournament.stack_inicial = int(stack_str) if stack_str.isdigit() else 10000
        
        tournament.save()
        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    data_str = tournament.data.strftime("%Y-%m-%dT%H:%M")
    return render(request, "tournament_form.html", {
        "season": season, 
        "tipos": tipos, 
        "tournament": tournament, 
        "data_str": data_str
    })