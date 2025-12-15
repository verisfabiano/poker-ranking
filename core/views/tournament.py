# core/views/tournament.py - COMPLETO CORRIGIDO

from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from ..models import (
    Season, Tournament, TournamentType, BlindStructure, 
    TournamentProduct, TournamentEntry, TournamentResult
)
from .auth import admin_required


def _get_decimal(request, field_name):
    """Tenta converter o valor do POST para Decimal."""
    val = request.POST.get(field_name, "").replace(",", ".").strip()
    if not val:
        return Decimal("0.00")
    try:
        return Decimal(val)
    except (ValueError, InvalidOperation):
        return Decimal("0.00")


# ============================================================
#  TIPOS DE TORNEIO
# ============================================================

@admin_required
def tournament_types_list(request):
    tipos = TournamentType.objects.order_by("nome")
    return render(request, "tournament_types_list.html", {"tipos": tipos})


@admin_required
def tournament_type_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        mult = request.POST.get("multiplicador", "1").replace(",", ".")
        try:
            mult = Decimal(mult)
        except:
            mult = Decimal("1")
        
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
        mult = request.POST.get("multiplicador", "1").replace(",", ".")
        try:
            tipo.multiplicador_pontos = Decimal(mult)
        except:
            pass
        
        tipo.usa_regras_padrao = request.POST.get("usa_regras_padrao") == "on"
        tipo.save()
        return HttpResponseRedirect(reverse("tournament_types_list"))
    return render(request, "tournament_type_form.html", {"tipo": tipo})


# ============================================================
#  TORNEIOS
# ============================================================

@admin_required
def season_tournaments(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tournaments = Tournament.objects.filter(season=season).order_by("-data")
    return render(request, "tournaments_list.html", {"season": season, "tournaments": tournaments})


@admin_required
def tournament_create(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tipos = TournamentType.objects.order_by("nome")
    blind_structures = BlindStructure.objects.order_by("nome")
    produtos_disponiveis = TournamentProduct.objects.order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome")
        tipo_id = request.POST.get("tipo_id")
        data_str = request.POST.get("data")
        status = request.POST.get("status", "AGENDADO")
        
        try:
            if data_str:
                data = datetime.fromisoformat(data_str)
            else:
                data = datetime.now()
        except (ValueError, TypeError):
            data = datetime.now()

        buyin = _get_decimal(request, "buyin")
        rake_type = request.POST.get("rake_type", "FIXO")
        
        # Parseando valores de rake baseado no tipo
        if rake_type == "MISTO":
            rake_valor = _get_decimal(request, "rake_valor_m")
            rake_percentual = _get_decimal(request, "rake_percentual_m")
        elif rake_type == "PERCENTUAL":
            rake_valor = Decimal("0.00")
            rake_percentual = _get_decimal(request, "rake_percentual")
        else:  # FIXO
            rake_valor = _get_decimal(request, "rake_valor")
            rake_percentual = Decimal("0.00")

        rebuy_valor = _get_decimal(request, "rebuy_valor")
        addon_valor = _get_decimal(request, "addon_valor")
        timechip_valor = _get_decimal(request, "timechip_valor")
        
        permite_rebuy = request.POST.get("permite_rebuy") == "on"
        permite_addon = request.POST.get("permite_addon") == "on"
        permite_rebuy_duplo = request.POST.get("permite_rebuy_duplo") == "on"
        max_rebuys = int(request.POST.get("max_rebuys", 0))
        blind_structure_id = request.POST.get("blind_structure") or None

        tournament = Tournament.objects.create(
            nome=nome,
            data=data,
            season=season,
            tipo_id=tipo_id,
            buyin=buyin,
            rake_type=rake_type,
            rake_valor=rake_valor,
            rake_percentual=rake_percentual,
            rebuy_valor=rebuy_valor,
            addon_valor=addon_valor,
            timechip_valor=timechip_valor,
            permite_rebuy=permite_rebuy,
            permite_addon=permite_addon,
            status=status,
            blind_structure_id=blind_structure_id,
            permite_rebuy_duplo=permite_rebuy_duplo,
            max_rebuys=max_rebuys,
        )
        
        # Adicionar produtos selecionados
        produtos_ids = request.POST.getlist("produtos")
        if produtos_ids:
            tournament.produtos.set(produtos_ids)

        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    context = {
        "season": season,
        "tournament": None,
        "tipos": tipos,
        "blind_structures": blind_structures,
        "produtos_disponiveis": produtos_disponiveis,
        "produtos_selecionados": [],
    }
    return render(request, "tournament_form.html", context)


@admin_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    tipos = TournamentType.objects.order_by("nome")
    blind_structures = BlindStructure.objects.order_by("nome")
    produtos_disponiveis = TournamentProduct.objects.order_by("nome")
    
    if request.method == "POST":
        tournament.nome = request.POST.get("nome")
        tournament.tipo_id = request.POST.get("tipo_id")
        data_str = request.POST.get("data")
        
        try:
            if data_str:
                tournament.data = datetime.fromisoformat(data_str)
        except (ValueError, TypeError):
            pass

        tournament.buyin = _get_decimal(request, "buyin")
        tournament.rake_type = request.POST.get("rake_type", "FIXO")
        
        if tournament.rake_type == "MISTO":
            tournament.rake_valor = _get_decimal(request, "rake_valor_m")
            tournament.rake_percentual = _get_decimal(request, "rake_percentual_m")
        elif tournament.rake_type == "PERCENTUAL":
            tournament.rake_valor = Decimal("0.00")
            tournament.rake_percentual = _get_decimal(request, "rake_percentual")
        else:
            tournament.rake_valor = _get_decimal(request, "rake_valor")
            tournament.rake_percentual = Decimal("0.00")

        tournament.rebuy_valor = _get_decimal(request, "rebuy_valor")
        tournament.addon_valor = _get_decimal(request, "addon_valor")
        tournament.timechip_valor = _get_decimal(request, "timechip_valor")
        tournament.permite_rebuy = request.POST.get("permite_rebuy") == "on"
        tournament.permite_addon = request.POST.get("permite_addon") == "on"
        tournament.permite_rebuy_duplo = request.POST.get("permite_rebuy_duplo") == "on"
        tournament.max_rebuys = int(request.POST.get("max_rebuys", 0))
        tournament.status = request.POST.get("status", "AGENDADO")
        tournament.blind_structure_id = request.POST.get("blind_structure") or None
        
        tournament.save()
        
        # Atualizar produtos selecionados
        produtos_ids = request.POST.getlist("produtos")
        tournament.produtos.set(produtos_ids)

        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    data_str = tournament.data.isoformat() if tournament.data else ""
    produtos_selecionados = list(tournament.produtos.values_list('id', flat=True))

    context = {
        "season": season,
        "tournament": tournament,
        "data_str": data_str,
        "tipos": tipos,
        "blind_structures": blind_structures,
        "produtos_disponiveis": produtos_disponiveis,
        "produtos_selecionados": produtos_selecionados,
    }
    return render(request, "tournament_form.html", context)


# ============================================================
#  GERENCIAMENTO DE INSCRIÇÕES
# ============================================================

@admin_required
def tournament_entries_manage(request, tournament_id):
    """Gerenciar inscrições e participantes do torneio"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season  # ADICIONAR ESTA LINHA
    
    mensagem = None
    mensagem_erro = None
    edicao_bloqueada = tournament.status in ['EM_ANDAMENTO', 'ENCERRADO', 'CANCELADO']
    
    if request.method == "POST":
        try:
            # Salvar confirmação admin
            if "save_admin_confirm" in request.POST:
                entries = TournamentEntry.objects.filter(tournament=tournament)
                for entry in entries:
                    confirmado = f"conf_admin_{entry.id}" in request.POST
                    entry.confirmado_pelo_admin = confirmado
                    entry.save()
                mensagem = "Confirmações atualizadas com sucesso!"
            
            # Remover entradas
            elif "remove_selected" in request.POST:
                ids_remover = request.POST.getlist("remover_entry_id")
                if ids_remover:
                    TournamentEntry.objects.filter(id__in=ids_remover).delete()
                    mensagem = f"{len(ids_remover)} jogador(es) removido(s)."
            
            # Confirmar todos os pedidos
            elif "confirm_all_requests" in request.POST:
                entries = TournamentEntry.objects.filter(
                    tournament=tournament,
                    confirmou_presenca=True,
                    confirmado_pelo_admin=False
                )
                entries.update(confirmado_pelo_admin=True)
                mensagem = f"{entries.count()} pedido(s) confirmado(s)!"
            
            # Adicionar jogador manualmente
            elif "add_player" in request.POST:
                novo_player_id = request.POST.get("novo_player_id", "").strip()
                if novo_player_id:
                    from core.models import Player
                    try:
                        player = Player.objects.get(id=novo_player_id)
                        # Verificar se já existe
                        if not TournamentEntry.objects.filter(tournament=tournament, player=player).exists():
                            TournamentEntry.objects.create(
                                tournament=tournament,
                                player=player,
                                confirmado_pelo_admin=True
                            )
                            mensagem = f"{player.nome} adicionado com sucesso!"
                        else:
                            mensagem_erro = f"{player.nome} já está inscrito neste torneio."
                    except Player.DoesNotExist:
                        mensagem_erro = "Jogador não encontrado."
                else:
                    mensagem_erro = "Selecione um jogador para adicionar."
        
        except Exception as e:
            mensagem_erro = f"Erro ao processar: {str(e)}"
    
    # Preparar contexto
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related('player')
    
    from core.models import Player
    inscritos_ids = TournamentEntry.objects.filter(tournament=tournament).values_list('player_id', flat=True)
    players_disponiveis = Player.objects.exclude(id__in=inscritos_ids).order_by('nome')
    
    context = {
        'tournament': tournament,
        'season': season,  # ADICIONAR ESTA LINHA
        'entries': entries,
        'players_disponiveis': players_disponiveis,
        'mensagem': mensagem,
        'mensagem_erro': mensagem_erro,
        'edicao_bloqueada': edicao_bloqueada,
    }
    return render(request, 'tournament_entries.html', context)

# ============================================================
#  LANÇAMENTO DE RESULTADOS
# ============================================================

@admin_required
def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    mensagem = None
    dados_post = {}  # Armazenar dados do POST
    
    if request.method == "POST":
        entries = TournamentEntry.objects.filter(tournament=tournament)
        
        for entry in entries:
            pid = entry.player.id
            
            # Verificar se participou
            participou = f"participou_{pid}" in request.POST
            
            # Captura dados
            pos_str = request.POST.get(f"pos_{pid}", "").strip()
            ajuste_str = request.POST.get(f"ajuste_{pid}", "").strip()
            prize_str = request.POST.get(f"prize_{pid}", "").replace(",", ".").strip()
            
            # Armazenar no dicionário para manter na tela
            dados_post[pid] = {
                'pos': pos_str,
                'ajuste': ajuste_str,
                'prize': prize_str,
                'participou': participou,
            }
            
            # Se participou e tem posição, cria/atualiza resultado
            if participou and pos_str:
                try:
                    res, _ = TournamentResult.objects.get_or_create(
                        tournament=tournament,
                        player=entry.player
                    )
                    
                    res.posicao = int(pos_str)
                    
                    # Prêmio
                    try:
                        res.premio = Decimal(prize_str) if prize_str else Decimal("0")
                    except:
                        res.premio = Decimal("0")
                    
                    # Ajuste de pontos
                    try:
                        res.pontos_participacao = int(ajuste_str) if ajuste_str else 0
                    except:
                        res.pontos_participacao = 0
                    
                    res.save()
                except Exception as e:
                    print(f"Erro ao salvar resultado: {e}")
            else:
                # Se não participou ou sem posição, remove resultado
                TournamentResult.objects.filter(tournament=tournament, player=entry.player).delete()
        
        mensagem = "✓ Resultados salvos com sucesso!"
    
    # GET + POST: Monta a lista com dados corretos
    linhas = []
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related("player").order_by("player__nome")
    for e in entries:
        r = TournamentResult.objects.filter(tournament=tournament, player=e.player).first()
        
        # Se foi POST, usar dados_post. Se não, usar dados do banco
        if dados_post and e.player.id in dados_post:
            linha_dict = {
                "player": e.player,
                "entry": e,
                "result": r,
                "pos_valor": dados_post[e.player.id]['pos'],
                "prize_valor": dados_post[e.player.id]['prize'],
                "ajuste_valor": dados_post[e.player.id]['ajuste'],
            }
        else:
            linha_dict = {
                "player": e.player,
                "entry": e,
                "result": r,
                "pos_valor": r.posicao if r else "",
                "prize_valor": r.premio if r else "0.00",
                "ajuste_valor": r.pontos_participacao if r else "",
            }
        linhas.append(linha_dict)
        
    return render(request, "tournament_results.html", {
        "tournament": tournament,
        "season": season,
        "linhas": linhas,
        "mensagem": mensagem,
    })