# core/views/financial.py - VERSÃO REFATORADA

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, F
from django.http import JsonResponse
from django.utils import timezone
from core.models import Tournament, TournamentEntry, TournamentResult, Season, PlayerProductPurchase
from ..decorators.tenant_decorators import admin_required
from .ranking import tenant_required


def calcular_financeiro_torneio(tournament):
    """
    Calcula financeiro completo de um torneio.
    FATURAMENTO BRUTO = Buy-in + Rebuys + Add-ons + Staff (TUDO)
    RAKE = calculado APENAS sobre (Buy-in + Rebuys + Add-ons), SEM staff
    POTE = (Buy-in + Rebuys + Add-ons) - Rake
    """
    entries = TournamentEntry.objects.filter(tournament=tournament, confirmado_pelo_admin=True)
    results = TournamentResult.objects.filter(tournament=tournament)
    
    count_players = entries.count()
    
    # Buy-ins confirmados
    total_buyin_bruto = count_players * tournament.buyin if tournament.buyin else Decimal('0')
    
    # Produtos que ENTRAM em premiação (Add-on, Rebuy, etc)
    total_produtos_premiacao = PlayerProductPurchase.objects.filter(
        tournament=tournament,
        product__entra_em_premiacao=True
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    # Produtos que NÃO entram (Jack Pot, Staff, etc) - receita pura, sem rake
    total_outros_produtos = PlayerProductPurchase.objects.filter(
        tournament=tournament,
        product__entra_em_premiacao=False
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    # FATURAMENTO BRUTO = TUDO (buy-in + produtos premiação + staff)
    faturamento_bruto = total_buyin_bruto + total_produtos_premiacao + total_outros_produtos
    
    # Base para RAKE = APENAS (buy-in + produtos premiação), SEM staff
    base_rake = total_buyin_bruto + total_produtos_premiacao
    
    # Calcular rake APENAS sobre base_rake (sem staff)
    rake_total = Decimal('0')
    if tournament.rake_type in ['FIXO', 'MISTO']:
        rake_total += count_players * tournament.rake_valor if tournament.rake_valor else Decimal('0')
    if tournament.rake_type in ['PERCENTUAL', 'MISTO']:
        rake_total += base_rake * (tournament.rake_percentual / 100)
    
    # POTE = base_rake - rake
    pote_total = base_rake - rake_total
    
    # Prêmios pagos (do TournamentResult)
    total_premios = results.aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or Decimal('0')
    
    return {
        'count_players': count_players,
        'buyin_total': total_buyin_bruto,
        'rake_total': rake_total,
        'pote_total': pote_total,
        'produtos_premiacao': total_produtos_premiacao,
        'outros_produtos': total_outros_produtos,
        'faturamento_bruto': faturamento_bruto,
        'premios_pagos': total_premios,
        'saldo': pote_total - total_premios,
    }


@admin_required
def tournament_financial(request, tournament_id):
    """Financeiro de um torneio específico"""
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related('player')
    results = TournamentResult.objects.filter(tournament=tournament).select_related('player')
    produtos = PlayerProductPurchase.objects.filter(tournament=tournament).select_related('player', 'product')
    
    financeiro = calcular_financeiro_torneio(tournament)
    
    # Calcular resultado: ENTRADAS - SAÍDAS
    resultado = financeiro['faturamento_bruto'] - financeiro['premios_pagos']
    
    # Criar um mapa de resultados por player_id para fácil acesso no template
    results_map = {r.player_id: r for r in results}
    
    # Criar um mapa de produtos por player_id
    produtos_por_jogador = {}
    for produto in produtos:
        if produto.player_id not in produtos_por_jogador:
            produtos_por_jogador[produto.player_id] = []
        produtos_por_jogador[produto.player_id].append(produto)
    
    # Preparar dados de inscritos com seus resultados e produtos
    inscritos_com_resultado = []
    for entry in entries:
        resultado_jogador = results_map.get(entry.player_id)
        produtos_jogador = produtos_por_jogador.get(entry.player_id, [])
        
        # Agrupar e contar produtos por tipo
        buyin_count = 0
        buyin_total = Decimal('0')
        rebuy_count = 0
        rebuy_total = Decimal('0')
        addon_count = 0
        addon_total = Decimal('0')
        
        for prod in produtos_jogador:
            if 'buy' in prod.product.nome.lower() and 'rebuy' not in prod.product.nome.lower():
                buyin_count += prod.quantidade
                buyin_total += prod.valor_pago
            elif 'rebuy' in prod.product.nome.lower():
                rebuy_count += prod.quantidade
                rebuy_total += prod.valor_pago
            elif 'addon' in prod.product.nome.lower():
                addon_count += prod.quantidade
                addon_total += prod.valor_pago
        
        total_gasto = buyin_total + rebuy_total + addon_total
        premio_recebido = resultado_jogador.premiacao_recebida if resultado_jogador else Decimal('0')
        resultado_jogador_valor = premio_recebido - total_gasto
        
        inscritos_com_resultado.append({
            'entry': entry,
            'resultado': resultado_jogador,
            'buyin_count': buyin_count,
            'buyin_total': buyin_total,
            'rebuy_count': rebuy_count,
            'rebuy_total': rebuy_total,
            'addon_count': addon_count,
            'addon_total': addon_total,
            'total_gasto': total_gasto,
            'resultado_valor': resultado_jogador_valor,
        })
    
    # Ordenar por posição (os com posição primeiro, depois os sem)
    inscritos_com_resultado.sort(
        key=lambda x: (
            x['resultado'].posicao if x['resultado'] and x['resultado'].posicao else 999,
        )
    )
    
    context = {
        'tournament': tournament,
        'entries': entries,
        'inscritos_com_resultado': inscritos_com_resultado,
        'results': results,
        'produtos': produtos,
        'financeiro': financeiro,
        'resultado': resultado,
    }
    
    return render(request, 'tournament_financial.html', context)


@admin_required
@admin_required
def financial_dashboard(request):
    """Dashboard financeiro geral com últimos 30 dias"""
    days = int(request.GET.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    tournaments = Tournament.objects.filter(tenant=request.tenant, data__gte=date_from).order_by('-data')
    
    financial_data = []
    totals = {
        'tournaments': 0,
        'players': 0,
        'buyin_total': Decimal('0'),
        'rake_total': Decimal('0'),
        'pote_total': Decimal('0'),
        'premios': Decimal('0'),
        'saldo': Decimal('0'),
    }
    
    for t in tournaments:
        fin = calcular_financeiro_torneio(t)
        
        # Contar quantidade de rebuys e addons
        rebuys_count = PlayerProductPurchase.objects.filter(
            tournament=t, product__nome__icontains='rebuy'
        ).count()
        addons_count = PlayerProductPurchase.objects.filter(
            tournament=t, product__nome__icontains='addon'
        ).count()
        
        # Somar valores separados
        rebuys_value = PlayerProductPurchase.objects.filter(
            tournament=t, product__nome__icontains='rebuy'
        ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
        
        addons_value = PlayerProductPurchase.objects.filter(
            tournament=t, product__nome__icontains='addon'
        ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
        
        staff_value = PlayerProductPurchase.objects.filter(
            tournament=t, product__nome__icontains='staff'
        ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
        
        # Faturamento bruto = buy-in + produtos premiacao + staff/outros
        faturamento_bruto_torneio = fin['buyin_total'] + fin['produtos_premiacao'] + fin['outros_produtos']
        
        # Resultado = Faturamento bruto - Premiação (SEM descontar rake, pois rake é lucro)
        resultado_torneio = faturamento_bruto_torneio - fin['premios_pagos']
        
        financial_data.append({
            'tournament': t,
            'count_players': fin['count_players'],
            'buyin_value': fin['buyin_total'],
            'rebuys_count': rebuys_count,
            'rebuys_value': rebuys_value,
            'addons_count': addons_count,
            'addons_value': addons_value,
            'staff_value': staff_value,
            'gross_total': faturamento_bruto_torneio,
            'rake_total': fin['rake_total'],
            'prize_paid': fin['premios_pagos'],  # Premiação efetivamente paga
            'resultado': resultado_torneio,  # Resultado = Faturamento - Premiação
        })
        
        totals['tournaments'] += 1
        totals['players'] += fin['count_players']
        totals['buyin_total'] += fin['buyin_total']
        totals['rake_total'] += fin['rake_total']
        totals['pote_total'] += fin['pote_total']
        totals['premios'] += fin['premios_pagos']
        totals['saldo'] += fin['saldo']
    
    # Calcular totais com TODOS os produtos
    total_produtos_premiacao = sum(calcular_financeiro_torneio(t)['produtos_premiacao'] for t in tournaments)
    total_outros_produtos = sum(calcular_financeiro_torneio(t)['outros_produtos'] for t in tournaments)
    
    # ENTRADAS = TUDO que foi arrecadado (buy-in + add-on + rebuy + staff)
    # Antes era chamado de "Faturamento Bruto"
    grand_total_entradas = totals['buyin_total'] + total_produtos_premiacao + total_outros_produtos
    
    # SAÍDAS = Prêmios pagos (+ futuras outras despesas como dealer, etc)
    # Antes era chamado de "Despesas"
    grand_total_saidas = totals['premios']
    
    # RESULTADO = ENTRADAS - SAÍDAS (simples assim)
    # NÃO subtraí rake do resultado, pois rake já é desconto implícito no pote
    grand_total_resultado = grand_total_entradas - grand_total_saidas
    
    context = {
        'days': days,
        'date_from': date_from,
        'financial_data': financial_data,
        'total_tournaments': totals['tournaments'],
        'grand_total_entradas': grand_total_entradas,  # Entradas = Faturamento Bruto
        'grand_total_saidas': grand_total_saidas,  # Saídas = Despesas (Prêmios)
        'grand_total_resultado': grand_total_resultado,  # Resultado = Entradas - Saídas
    }
    
    return render(request, 'financial_dashboard.html', context)


@admin_required
def season_financial(request, season_id):
    """Financeiro completo de uma temporada"""
    season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
    tournaments = Tournament.objects.filter(season=season, tenant=request.tenant).order_by('-data')
    
    season_data = []
    season_totals = {
        'tournaments': 0,
        'players': 0,
        'buyin_total': Decimal('0'),
        'rake_total': Decimal('0'),
        'pote_total': Decimal('0'),
        'premios': Decimal('0'),
        'saldo': Decimal('0'),
    }
    
    for t in tournaments:
        fin = calcular_financeiro_torneio(t)
        season_data.append({
            'tournament': t,
            'financeiro': fin,
        })
        
        season_totals['tournaments'] += 1
        season_totals['players'] += fin['count_players']
        season_totals['buyin_total'] += fin['buyin_total']
        season_totals['rake_total'] += fin['rake_total']
        season_totals['pote_total'] += fin['pote_total']
        season_totals['premios'] += fin['premios_pagos']
        season_totals['saldo'] += fin['saldo']
    
    context = {
        'season': season,
        'season_data': season_data,
        'season_totals': season_totals,
    }
    
    return render(request, 'season_financial.html', context)


@admin_required
def financial_by_period(request):
    """Financeiro por período customizável"""
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
    
    tournaments = Tournament.objects.filter(
        tenant=request.tenant,
        data__date__gte=start_date,
        data__date__lte=end_date
    ).order_by('-data')
    
    period_data = []
    period_totals = {
        'buyin_total': Decimal('0'),
        'rake_total': Decimal('0'),
        'pote_total': Decimal('0'),
        'premios': Decimal('0'),
        'saldo': Decimal('0'),
    }
    
    for t in tournaments:
        fin = calcular_financeiro_torneio(t)
        period_data.append({
            'tournament': t,
            'financeiro': fin,
        })
        
        period_totals['buyin_total'] += fin['buyin_total']
        period_totals['rake_total'] += fin['rake_total']
        period_totals['pote_total'] += fin['pote_total']
        period_totals['premios'] += fin['premios_pagos']
        period_totals['saldo'] += fin['saldo']
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'start_date_str': start_date_str,
        'end_date_str': end_date_str,
        'period_data': period_data,
        'period_totals': period_totals,
    }
    
    return render(request, 'financial_by_period.html', context)


@admin_required
def api_financial_summary(request):
    """API JSON com resumo financeiro para gráficos"""
    days = int(request.GET.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    tournaments = Tournament.objects.filter(tenant=request.tenant, data__gte=date_from).order_by('data__date')
    
    daily_data = {}
    for t in tournaments:
        date_key = t.data.date().isoformat()
        fin = calcular_financeiro_torneio(t)
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                'tournaments': 0,
                'players': 0,
                'rake': 0,
                'saldo': 0,
            }
        
        daily_data[date_key]['tournaments'] += 1
        daily_data[date_key]['players'] += fin['count_players']
        daily_data[date_key]['rake'] += float(fin['rake_total'])
        daily_data[date_key]['saldo'] += float(fin['saldo'])
    
    return JsonResponse({
        'days': days,
        'daily_data': daily_data,
    })