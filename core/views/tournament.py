# core/views/tournament.py - COMPLETO CORRIGIDO

from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ..models import (
    Season, Tournament, TournamentType, BlindStructure, 
    TournamentProduct, TournamentEntry, TournamentResult, PlayerProductPurchase, Player, TournamentPlayerPurchase
)
from .ranking import tenant_required
from ..decorators.tenant_decorators import admin_required


def _get_decimal(request, field_name):
    """Tenta converter o valor do POST para Decimal."""
    val = request.POST.get(field_name, "").replace(",", ".").strip()
    if not val:
        return Decimal("0.00")
    try:
        return Decimal(val)
    except (ValueError, InvalidOperation):
        return Decimal("0.00")


@admin_required
def tournament_dashboard(request):
    """Dashboard com abas para gerenciar torneios por status"""
    if not request.tenant:
        return HttpResponseRedirect(reverse('login'))
    
    tournaments_agendados = Tournament.objects.filter(
        tenant=request.tenant,
        status='AGENDADO'
    ).order_by('data')
    
    tournaments_andamento = Tournament.objects.filter(
        tenant=request.tenant,
        status='EM_ANDAMENTO'
    ).order_by('-data')
    
    tournaments_finalizados = Tournament.objects.filter(
        tenant=request.tenant,
        status='FINALIZADO'
    ).order_by('-data')
    
    context = {
        'tournaments_agendados': tournaments_agendados,
        'tournaments_andamento': tournaments_andamento,
        'tournaments_finalizados': tournaments_finalizados,
    }
    
    return render(request, 'tournament_dashboard.html', context)


# ============================================================
#  TIPOS DE TORNEIO
# ============================================================

@admin_required
def tournament_types_list(request):
    if not request.tenant:
        return HttpResponseRedirect(reverse('login'))
    
    tipos = TournamentType.objects.filter(tenant=request.tenant).order_by("nome")
    return render(request, "tournament_types_list.html", {"tipos": tipos})


@admin_required
def tournament_type_create(request):
    if not request.tenant:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        multiplicador = request.POST.get("multiplicador_pontos", "1.00").strip()
        
        try:
            multiplicador = Decimal(multiplicador)
        except:
            multiplicador = Decimal("1.00")
        
        if nome:
            TournamentType.objects.create(
                nome=nome,
                multiplicador_pontos=multiplicador, 
                usa_regras_padrao=request.POST.get("usa_regras_padrao") == "on",
                tenant=request.tenant
            )
        return HttpResponseRedirect(reverse("tournament_types_list"))
    return render(request, "tournament_type_form.html", {"tipo": None})


@admin_required
def tournament_type_edit(request, tipo_id):
    tipo = get_object_or_404(TournamentType, id=tipo_id, tenant=request.tenant)
    if request.method == "POST":
        tipo.nome = request.POST.get("nome", "")
        
        multiplicador = request.POST.get("multiplicador_pontos", "1.00").strip()
        try:
            tipo.multiplicador_pontos = Decimal(multiplicador)
        except:
            tipo.multiplicador_pontos = Decimal("1.00")
        
        tipo.usa_regras_padrao = request.POST.get("usa_regras_padrao") == "on"
        tipo.save()
        return HttpResponseRedirect(reverse("tournament_types_list"))
    return render(request, "tournament_type_form.html", {"tipo": tipo})


# ============================================================
#  TORNEIOS
# ============================================================

@admin_required
def tournaments_list_all(request):
    """Lista todos os torneios do tenant, agrupados por temporada"""
    if not request.tenant:
        return HttpResponseRedirect(reverse('login'))
    
    seasons = Season.objects.filter(tenant=request.tenant).order_by("-data_inicio")
    
    # Criar dicionário com torneios por temporada
    seasons_with_tournaments = []
    for season in seasons:
        tournaments = Tournament.objects.filter(season=season, tenant=request.tenant).order_by("-data")
        seasons_with_tournaments.append({
            'season': season,
            'tournaments': tournaments,
            'total': tournaments.count()
        })
    
    return render(request, "tournaments_list_all.html", {
        "seasons_with_tournaments": seasons_with_tournaments
    })


@admin_required
def season_tournaments(request, season_id):
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    tournaments = Tournament.objects.filter(season=season, tenant=request.tenant).order_by("-data")
    return render(request, "tournaments_list.html", {"season": season, "tournaments": tournaments})


@admin_required
def tournament_create(request, season_id):
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    tipos = TournamentType.objects.order_by("nome")
    # Filtrar apenas blind_structures do tenant que tem níveis definidos
    blind_structures = BlindStructure.objects.filter(
        tenant=request.tenant,
        levels__isnull=False
    ).distinct().order_by("nome")
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
        rebuy_duplo_valor = _get_decimal(request, "rebuy_duplo_valor")
        addon_valor = _get_decimal(request, "addon_valor")
        staff_valor = _get_decimal(request, "staff_valor")
        
        buyin_chips = request.POST.get("buyin_chips") or None
        rebuy_chips = request.POST.get("rebuy_chips") or None
        rebuy_duplo_chips = request.POST.get("rebuy_duplo_chips") or None
        addon_chips = request.POST.get("addon_chips") or None
        staff_chips = request.POST.get("staff_chips") or None
        timechip_chips = request.POST.get("timechip_chips") or None
        
        permite_rebuy = request.POST.get("permite_rebuy") == "on"
        permite_rebuy_duplo = request.POST.get("permite_rebuy_duplo") == "on"
        permite_addon = request.POST.get("permite_addon") == "on"
        blind_structure_id = request.POST.get("blind_structure") or None

        tournament = Tournament.objects.create(
            nome=nome,
            data=data,
            season=season,
            tipo_id=tipo_id,
            buyin=buyin,
            buyin_chips=int(buyin_chips) if buyin_chips else None,
            rake_type=rake_type,
            rake_valor=rake_valor,
            rake_percentual=rake_percentual,
            rebuy_valor=rebuy_valor,
            rebuy_chips=int(rebuy_chips) if rebuy_chips else None,
            rebuy_duplo_valor=rebuy_duplo_valor,
            rebuy_duplo_chips=int(rebuy_duplo_chips) if rebuy_duplo_chips else None,
            addon_valor=addon_valor,
            addon_chips=int(addon_chips) if addon_chips else None,
            staff_valor=staff_valor,
            staff_chips=int(staff_chips) if staff_chips else None,
            staff_obrigatorio=request.POST.get("staff_obrigatorio") == "on",
            timechip_chips=int(timechip_chips) if timechip_chips else None,
            permite_rebuy=permite_rebuy,
            permite_rebuy_duplo=permite_rebuy_duplo,
            permite_addon=permite_addon,
            status=status,
            blind_structure_id=blind_structure_id,
            tenant=request.tenant,
        )
        
        # Adicionar produtos selecionados
        produtos_ids = request.POST.getlist("produtos")
        if produtos_ids:
            tournament.produtos.set(produtos_ids)

        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    context = {
        "season": season,
        "tournament": None,
        "data_str": "",
        "buyin_str": "",
        "rake_valor_str": "",
        "rake_percentual_str": "",
        "rebuy_valor_str": "",
        "rebuy_duplo_valor_str": "",
        "addon_valor_str": "",
        "staff_valor_str": "",
        "tipos": tipos,
        "blind_structures": blind_structures,
        "produtos_disponiveis": produtos_disponiveis,
        "produtos_selecionados": [],
    }
    return render(request, "tournament_form.html", context)


@admin_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    season = tournament.season
    tipos = TournamentType.objects.order_by("nome")
    # Filtrar apenas blind_structures do tenant que tem níveis definidos
    blind_structures = BlindStructure.objects.filter(
        tenant=request.tenant,
        levels__isnull=False
    ).distinct().order_by("nome")
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
        tournament.buyin_chips = request.POST.get("buyin_chips") or None
        if tournament.buyin_chips:
            tournament.buyin_chips = int(tournament.buyin_chips)
        
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
        tournament.rebuy_chips = request.POST.get("rebuy_chips") or None
        if tournament.rebuy_chips:
            tournament.rebuy_chips = int(tournament.rebuy_chips)
        
        tournament.rebuy_duplo_valor = _get_decimal(request, "rebuy_duplo_valor")
        tournament.rebuy_duplo_chips = request.POST.get("rebuy_duplo_chips") or None
        if tournament.rebuy_duplo_chips:
            tournament.rebuy_duplo_chips = int(tournament.rebuy_duplo_chips)
        
        tournament.addon_valor = _get_decimal(request, "addon_valor")
        tournament.addon_chips = request.POST.get("addon_chips") or None
        if tournament.addon_chips:
            tournament.addon_chips = int(tournament.addon_chips)
        
        tournament.staff_valor = _get_decimal(request, "staff_valor")
        tournament.staff_chips = request.POST.get("staff_chips") or None
        if tournament.staff_chips:
            tournament.staff_chips = int(tournament.staff_chips)
        tournament.staff_obrigatorio = request.POST.get("staff_obrigatorio") == "on"
        
        tournament.timechip_chips = request.POST.get("timechip_chips") or None
        if tournament.timechip_chips:
            tournament.timechip_chips = int(tournament.timechip_chips)
        
        tournament.permite_rebuy = request.POST.get("permite_rebuy") == "on"
        tournament.permite_rebuy_duplo = request.POST.get("permite_rebuy_duplo") == "on"
        tournament.permite_addon = request.POST.get("permite_addon") == "on"
        tournament.status = request.POST.get("status", "AGENDADO")
        
        # Blind structure pode ser alterada apenas se o torneio não começou
        if tournament.status == "AGENDADO":
            tournament.blind_structure_id = request.POST.get("blind_structure") or None
        # Se o torneio já começou, mantém a estrutura de blinds existente
        
        tournament.save()
        
        # Atualizar produtos selecionados
        produtos_ids = request.POST.getlist("produtos")
        tournament.produtos.set(produtos_ids)

        return HttpResponseRedirect(reverse("season_tournaments", args=[season.id]))

    # Converter data para formato datetime-local (sem timezone)
    data_str = ""
    if tournament.data:
        # Remove timezone para datetime-local
        data_str = tournament.data.replace(tzinfo=None).isoformat()
    
    # Formatar números com ponto para HTML5 type=number
    buyin_str = f"{float(tournament.buyin):.2f}" if tournament.buyin else ""
    rake_valor_str = f"{float(tournament.rake_valor):.2f}" if tournament.rake_valor else ""
    rake_percentual_str = f"{float(tournament.rake_percentual):.2f}" if tournament.rake_percentual else ""
    rebuy_valor_str = f"{float(tournament.rebuy_valor):.2f}" if tournament.rebuy_valor else ""
    rebuy_duplo_valor_str = f"{float(tournament.rebuy_duplo_valor):.2f}" if tournament.rebuy_duplo_valor else ""
    addon_valor_str = f"{float(tournament.addon_valor):.2f}" if tournament.addon_valor else ""
    staff_valor_str = f"{float(tournament.staff_valor):.2f}" if tournament.staff_valor else ""
    
    produtos_selecionados = list(tournament.produtos.values_list('id', flat=True))

    context = {
        "season": season,
        "tournament": tournament,
        "data_str": data_str,
        "buyin_str": buyin_str,
        "rake_valor_str": rake_valor_str,
        "rake_percentual_str": rake_percentual_str,
        "rebuy_valor_str": rebuy_valor_str,
        "rebuy_duplo_valor_str": rebuy_duplo_valor_str,
        "addon_valor_str": addon_valor_str,
        "staff_valor_str": staff_valor_str,
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
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    season = tournament.season
    
    mensagem = None
    mensagem_erro = None
    # Bloqueio apenas para ENCERRADO e CANCELADO (permite operações durante EM_ANDAMENTO)
    edicao_bloqueada = tournament.status in ['ENCERRADO', 'CANCELADO']
    entrada_bloqueada = tournament.status in ['ENCERRADO', 'CANCELADO']
    
    if request.method == "POST":
        try:
            # Adicionar produtos ao jogador
            if "add_products" in request.POST:
                player_id = request.POST.get("player_id", "").strip()
                product_ids = request.POST.getlist("products")
                
                if player_id and product_ids:
                    from core.models import Player, TournamentProduct, PlayerProductPurchase
                    
                    try:
                        player = Player.objects.get(id=player_id, tenant=request.tenant)
                        
                        for product_id in product_ids:
                            try:
                                product = TournamentProduct.objects.get(id=product_id, tenant=request.tenant)
                                # Criar ou atualizar compra
                                purchase, created = PlayerProductPurchase.objects.get_or_create(
                                    tournament=tournament,
                                    player=player,
                                    product=product,
                                    defaults={
                                        'tenant': request.tenant,
                                        'quantidade': 1,
                                        'valor_pago': product.valor
                                    }
                                )
                            except TournamentProduct.DoesNotExist:
                                pass
                        
                        mensagem = f"Produtos adicionados a {player.nome} com sucesso!"
                    except Player.DoesNotExist:
                        mensagem_erro = "Jogador não encontrado."
                else:
                    mensagem_erro = "Selecione pelo menos um produto."
            
            # Salvar confirmação admin
            elif "save_admin_confirm" in request.POST:
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
                    from core.models import Player, TournamentProduct, PlayerProductPurchase
                    try:
                        player = Player.objects.get(id=novo_player_id)
                        # Verificar se já existe
                        if not TournamentEntry.objects.filter(tournament=tournament, player=player).exists():
                            entry = TournamentEntry.objects.create(
                                tournament=tournament,
                                player=player,
                                confirmado_pelo_admin=True
                            )
                            
                            # Se STAFF é obrigatório, registrar como compra automaticamente
                            if tournament.staff_obrigatorio and tournament.staff_valor > 0:
                                # Procurar ou criar um produto "STAFF" genérico
                                staff_product, created = TournamentProduct.objects.get_or_create(
                                    nome="STAFF",
                                    tenant=request.tenant,
                                    defaults={
                                        'descricao': 'Taxa de STAFF obrigatória',
                                        'valor': tournament.staff_valor,
                                        'entra_em_premiacao': False
                                    }
                                )
                                # Atualizar valor se mudou
                                if staff_product.valor != tournament.staff_valor:
                                    staff_product.valor = tournament.staff_valor
                                    staff_product.save()
                                
                                # Registrar compra do STAFF
                                PlayerProductPurchase.objects.get_or_create(
                                    tournament=tournament,
                                    player=player,
                                    product=staff_product,
                                    defaults={
                                        'tenant': request.tenant,
                                        'quantidade': 1,
                                        'valor_pago': tournament.staff_valor
                                    }
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
    
    from core.models import Player, TournamentProduct, PlayerProductPurchase
    inscritos_ids = TournamentEntry.objects.filter(tournament=tournament).values_list('player_id', flat=True)
    players_disponiveis = Player.objects.filter(tenant=request.tenant).exclude(id__in=inscritos_ids).order_by('nome')
    
    # Obter produtos e compras
    products = TournamentProduct.objects.filter(tenant=request.tenant).order_by('nome')
    purchases_dict = {}
    for entry in entries:
        purchases = PlayerProductPurchase.objects.filter(
            tournament=tournament,
            player=entry.player
        ).values_list('product_id', flat=True)
        purchases_dict[entry.player.id] = list(purchases)
    
    # Adicionar info de compras a cada entrada
    for entry in entries:
        entry.product_purchases = purchases_dict.get(entry.player.id, [])
    
    context = {
        'tournament': tournament,
        'season': season,
        'entries': entries,
        'players_disponiveis': players_disponiveis,
        'products': products,
        'mensagem': mensagem,
        'mensagem_erro': mensagem_erro,
        'edicao_bloqueada': edicao_bloqueada,
        'entrada_bloqueada': entrada_bloqueada,
    }
    return render(request, 'tournament_entries.html', context)

# ============================================================
#  LANÇAMENTO DE RESULTADOS
# ============================================================

@admin_required
def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
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
                "prize_valor": f"{float(r.premiacao_recebida):.2f}" if r and r.premiacao_recebida else "0.00",
                "ajuste_valor": r.pontos_participacao if r else "",
            }
        linhas.append(linha_dict)
        
    return render(request, "tournament_results.html", {
        "tournament": tournament,
        "season": season,
        "linhas": linhas,
        "mensagem": mensagem,
    })


# ============================================================
#  GERENCIAMENTO DE PRODUTOS
# ============================================================

@admin_required
def tournament_products_list(request):
    """Lista todos os produtos do tenant"""
    products = TournamentProduct.objects.filter(tenant=request.tenant).order_by('nome')
    
    context = {
        'products': products,
        'total': products.count(),
    }
    
    return render(request, 'tournament_products_list.html', context)


@admin_required
def tournament_product_create(request):
    """Criar novo produto"""
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        valor_str = request.POST.get('valor', '0')
        entra_em_premiacao = 'entra_em_premiacao' in request.POST
        
        if not nome:
            return render(request, 'tournament_product_form.html', {
                'error': 'Nome do produto é obrigatório'
            })
        
        try:
            valor = Decimal(valor_str)
            if valor < 0:
                raise ValueError('Valor não pode ser negativo')
        except (InvalidOperation, ValueError):
            return render(request, 'tournament_product_form.html', {
                'error': 'Valor inválido'
            })
        
        product, created = TournamentProduct.objects.get_or_create(
            nome=nome,
            tenant=request.tenant,
            defaults={
                'descricao': descricao,
                'valor': valor,
                'entra_em_premiacao': entra_em_premiacao
            }
        )
        
        if not created:
            return render(request, 'tournament_product_form.html', {
                'error': f'Produto "{nome}" já existe'
            })
        
        return redirect('tournament_products_list')
    
    return render(request, 'tournament_product_form.html')


@admin_required
def tournament_product_edit(request, product_id):
    """Editar produto"""
    product = get_object_or_404(TournamentProduct, id=product_id, tenant=request.tenant)
    
    if request.method == 'POST':
        product.nome = request.POST.get('nome', '').strip()
        product.descricao = request.POST.get('descricao', '').strip()
        product.entra_em_premiacao = 'entra_em_premiacao' in request.POST
        
        try:
            valor_str = request.POST.get('valor', '0')
            product.valor = Decimal(valor_str)
            if product.valor < 0:
                raise ValueError('Valor não pode ser negativo')
        except (InvalidOperation, ValueError):
            return render(request, 'tournament_product_form.html', {
                'product': product,
                'error': 'Valor inválido'
            })
        
        if not product.nome:
            return render(request, 'tournament_product_form.html', {
                'product': product,
                'error': 'Nome do produto é obrigatório'
            })
        
        product.save()
        return redirect('tournament_products_list')
    
    context = {
        'product': product,
        'edit': True
    }
    
    return render(request, 'tournament_product_form.html', context)


@admin_required
def tournament_product_delete(request, product_id):
    """Deletar produto"""
    product = get_object_or_404(TournamentProduct, id=product_id, tenant=request.tenant)
    
    if request.method == 'POST':
        product.delete()
        return redirect('tournament_products_list')
    
    context = {
        'product': product
    }
    
    return render(request, 'tournament_product_confirm_delete.html', context)


@admin_required
def tournament_product_sales(request, tournament_id):
    """Gerenciar vendas de produtos para um torneio"""
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related('player')
    products = TournamentProduct.objects.filter(tenant=request.tenant).order_by('nome')
    
    # Buscar compras existentes
    purchases = PlayerProductPurchase.objects.filter(tournament=tournament).select_related('player', 'product')
    purchases_dict = {}
    for p in purchases:
        key = f"{p.player_id}_{p.product_id}"
        purchases_dict[key] = p
    
    # Preparar dados para template
    sales_data = []
    for entry in entries:
        player_products = []
        for product in products:
            key = f"{entry.player_id}_{product.id}"
            purchase = purchases_dict.get(key)
            
            player_products.append({
                'product': product,
                'purchased': purchase is not None,
                'quantity': purchase.quantidade if purchase else 0,
                'valor_pago': purchase.valor_pago if purchase else Decimal('0'),
                'purchase_id': purchase.id if purchase else None,
            })
        
        sales_data.append({
            'entry': entry,
            'products': player_products,
        })
    
    context = {
        'tournament': tournament,
        'products': products,
        'sales_data': sales_data,
        'total_entries': entries.count(),
    }
    
    return render(request, 'tournament_product_sales.html', context)


@admin_required
def tournament_product_purchase_add(request):
    """Adicionar compra de produto"""
    if request.method == 'POST':
        tournament_id = request.POST.get('tournament_id')
        player_id = request.POST.get('player_id')
        product_id = request.POST.get('product_id')
        quantidade = int(request.POST.get('quantidade', '1'))
        valor_pago_str = request.POST.get('valor_pago', '0')
        
        try:
            valor_pago = Decimal(valor_pago_str)
        except (InvalidOperation, ValueError):
            return JsonResponse({'success': False, 'error': 'Valor inválido'})
        
        tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
        player = get_object_or_404(Player, id=player_id, tenant=request.tenant)
        product = get_object_or_404(TournamentProduct, id=product_id, tenant=request.tenant)
        
        purchase, created = PlayerProductPurchase.objects.get_or_create(
            tournament=tournament,
            player=player,
            product=product,
            defaults={
                'tenant': request.tenant,
                'quantidade': quantidade,
                'valor_pago': valor_pago
            }
        )
        
        if not created:
            # Atualizar se já existe
            purchase.quantidade = quantidade
            purchase.valor_pago = valor_pago
            purchase.save()
        
        return redirect('tournament_product_sales', tournament_id=tournament_id)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@admin_required
def tournament_product_purchase_delete(request, purchase_id):
    """Deletar compra de produto"""
    purchase = get_object_or_404(PlayerProductPurchase, id=purchase_id, tenant=request.tenant)
    tournament_id = purchase.tournament_id
    
    if request.method == 'POST':
        purchase.delete()
        return redirect('tournament_product_sales', tournament_id=tournament_id)
    
    context = {
        'purchase': purchase
    }
    
    return render(request, 'tournament_product_purchase_confirm_delete.html', context)


# ============================================================
#  REBUY E ADD-ON
# ============================================================

@admin_required
@tenant_required
def tournament_add_rebuy_addon(request, tournament_id):
    """
    AJAX: Adicionar rebuy, rebuy duplo, addon ou time chip a um jogador
    POST JSON: {"player_id": int, "tipo": "REBUY|REBUY_DUPLO|ADDON|TIME_CHIP"}
    
    Regras:
    - REBUY: quantidade ilimitada
    - REBUY_DUPLO: quantidade ilimitada (com valor diferenciado)  
    - ADDON: máximo 1 por jogador
    - TIME_CHIP: máximo 1 por jogador (sem valor monetário)
    
    SALVA EM: PlayerProductPurchase (não em TournamentPlayerPurchase) para integração com sistema financeiro
    """
    import json
    from ..models import TournamentProduct, PlayerProductPurchase
    
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=400)
    
    try:
        data = json.loads(request.body)
        player_id = data.get('player_id')
        tipo = data.get('tipo')  # REBUY, REBUY_DUPLO, ADDON ou TIME_CHIP
        
        # Validações
        if not player_id or not tipo:
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
        
        if tipo not in ['REBUY', 'REBUY_DUPLO', 'ADDON', 'TIME_CHIP']:
            return JsonResponse({'success': False, 'error': 'Tipo inválido'}, status=400)
        
        # Obter valor e validar permissão
        if tipo == 'REBUY':
            if not tournament.permite_rebuy:
                return JsonResponse({'success': False, 'error': 'Rebuy não permitido neste torneio'}, status=400)
            valor = tournament.rebuy_valor or 0
            entra_em_premiacao = True  # Rebuy entra no pote
        elif tipo == 'REBUY_DUPLO':
            if not tournament.permite_rebuy_duplo:
                return JsonResponse({'success': False, 'error': 'Rebuy Duplo não permitido neste torneio'}, status=400)
            # Usar valor customizado ou 2x o rebuy simples
            valor = tournament.rebuy_duplo_valor or (tournament.rebuy_valor * 2 if tournament.rebuy_valor else 0)
            entra_em_premiacao = True  # Rebuy Duplo entra no pote
        elif tipo == 'ADDON':
            if not tournament.permite_addon:
                return JsonResponse({'success': False, 'error': 'Add-on não permitido neste torneio'}, status=400)
            valor = tournament.addon_valor or 0
            entra_em_premiacao = True  # Add-on entra no pote
        else:  # TIME_CHIP
            if not tournament.timechip_chips:
                return JsonResponse({'success': False, 'error': 'Time Chip não configurado neste torneio'}, status=400)
            valor = 0  # TIME_CHIP não tem valor monetário
            entra_em_premiacao = False  # Time Chip não entra no pote (sem valor)
        
        if valor < 0:  # Permite 0 para TIME_CHIP
            return JsonResponse({'success': False, 'error': f'{tipo.replace("_", " ").title()} não configurado'}, status=400)
        
        # Obter jogador
        player = Player.objects.get(id=player_id, tenant=request.tenant)
        
        # Validação especial para Add-on e Time Chip: máximo 1
        if tipo in ['ADDON', 'TIME_CHIP']:
            # Contar quantas compras já existem deste tipo
            existing_count = PlayerProductPurchase.objects.filter(
                tournament=tournament,
                player=player,
                product__nome=tipo  # Procura por produto com nome = tipo
            ).count()
            
            if existing_count > 0:
                return JsonResponse({
                    'success': False, 
                    'error': f'Este jogador já tem {tipo.replace("_", " ").lower()} neste torneio (máximo 1 permitido)'
                }, status=400)
        
        # IMPORTANTE: Criar ou obter um TournamentProduct para este tipo
        # Isso permite que o sistema financeiro conte as compras
        product, product_created = TournamentProduct.objects.get_or_create(
            nome=tipo,
            tenant=request.tenant,
            defaults={
                'descricao': f'{tipo.replace("_", " ").title()} do torneio',
                'valor': valor,
                'entra_em_premiacao': entra_em_premiacao
            }
        )
        
        # Se produto já existia mas o valor mudou, atualizar
        if not product_created and product.valor != valor:
            product.valor = valor
            product.save()
        
        # SALVAR EM PlayerProductPurchase (integrado com sistema financeiro)
        # Usar um identifier único para evitar conflitos
        purchase_key = f"{tournament.id}_{player_id}_{tipo}"
        purchase, created = PlayerProductPurchase.objects.get_or_create(
            tournament=tournament,
            player=player,
            product=product,
            defaults={
                'tenant': request.tenant,
                'quantidade': 1,
                'valor_pago': valor
            }
        )
        
        if not created:
            # Se já existe, incrementar quantidade
            purchase.quantidade += 1
            purchase.valor_pago = valor * purchase.quantidade  # Atualizar valor total
            purchase.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{tipo.replace("_", " ").title()} adicionado! ({purchase.quantidade}x)',
            'quantidade': purchase.quantidade,
            'valor_total': str(float(purchase.valor_pago))
        })
    
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Jogador não encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def tournament_remove_rebuy_addon(request, tournament_id):
    """
    AJAX: Remover 1 unidade de rebuy, rebuy duplo, addon ou time chip
    POST JSON: {"player_id": int, "tipo": "REBUY|REBUY_DUPLO|ADDON|TIME_CHIP"}
    
    Decrementa quantidade em 1. Se chegar a 0, deleta o registro.
    AGORA TRABALHA COM PlayerProductPurchase (não mais TournamentPlayerPurchase)
    """
    import json
    from ..models import PlayerProductPurchase
    
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=400)
    
    try:
        data = json.loads(request.body)
        player_id = data.get('player_id')
        tipo = data.get('tipo')
        
        if not player_id or not tipo:
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
        
        if tipo not in ['REBUY', 'REBUY_DUPLO', 'ADDON', 'TIME_CHIP']:
            return JsonResponse({'success': False, 'error': 'Tipo inválido'}, status=400)
        
        # Obter jogador
        player = Player.objects.get(id=player_id, tenant=request.tenant)
        
        # Buscar compra existente em PlayerProductPurchase
        purchase = PlayerProductPurchase.objects.filter(
            tournament=tournament,
            player=player,
            product__nome=tipo  # Produto com nome = tipo
        ).first()
        
        if not purchase:
            return JsonResponse({
                'success': False, 
                'error': f'Nenhuma compra de {tipo.replace("_", " ").title()} encontrada'
            }, status=400)
        
        # Decrementar quantidade
        if purchase.quantidade > 1:
            purchase.quantidade -= 1
            purchase.valor_pago = purchase.product.valor * purchase.quantidade  # Atualizar valor total
            purchase.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{tipo.replace("_", " ").title()} removido! ({purchase.quantidade}x)',
                'quantidade': purchase.quantidade,
                'valor_total': str(float(purchase.valor_pago))
            })
        else:
            # Deletar se quantidade era 1
            purchase.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{tipo.replace("_", " ").title()} cancelado!',
                'quantidade': 0,
                'valor_total': '0.00'
            })
    
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Jogador não encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)