# core/views/financial.py - VERSÃO REFATORADA

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, F
from django.http import JsonResponse
from django.utils import timezone
from core.models import Tournament, TournamentEntry, TournamentResult, Season, PlayerProductPurchase
from .auth import admin_required


def calcular_financeiro_torneio(tournament):
    """
    Calcula financeiro completo de um torneio.
    Retorna dicionário com gross, rake, prize_pool.
    """
    entries = TournamentEntry.objects.filter(tournament=tournament, confirmado_pelo_admin=True)
    results = TournamentResult.objects.filter(tournament=tournament)
    
    count_players = entries.count()
    
    # Buy-ins confirmados
    total_buyin_bruto = count_players * tournament.buyin if tournament.buyin else Decimal('0')
    rake_buyin = count_players * tournament.rake_valor if tournament.rake_type in ['FIXO', 'MISTO'] else Decimal('0')
    if tournament.rake_type in ['PERCENTUAL', 'MISTO']:
        rake_buyin += total_buyin_bruto * (tournament.rake_percentual / 100)
    
    pote_buyin = total_buyin_bruto - rake_buyin
    
    # Prêmios pagos (do TournamentResult)
    total_premios = results.aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or Decimal('0')
    
    # Produtos vendidos (jackpot, bounty, etc)
    total_produtos = PlayerProductPurchase.objects.filter(tournament=tournament).aggregate(
        Sum('valor_pago')
    )['valor_pago__sum'] or Decimal('0')
    
    return {
        'count_players': count_players,
        'buyin_total': total_buyin_bruto,
        'rake_total': rake_buyin,
        'pote_total': pote_buyin,
        'premios_pagos': total_premios,
        'produtos_vendidos': total_produtos,
        'saldo': (pote_buyin + total_produtos) - total_premios,
    }


@admin_required
def tournament_financial(request, tournament_id):
    """Financeiro de um torneio específico"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related('player')
    results = TournamentResult.objects.filter(tournament=tournament)
    produtos = PlayerProductPurchase.objects.filter(tournament=tournament).select_related('player', 'product')
    
    financeiro = calcular_financeiro_torneio(tournament)
    
    context = {
        'tournament': tournament,
        'entries': entries,
        'results': results,
        'produtos': produtos,
        'financeiro': financeiro,
    }
    
    return render(request, 'tournament_financial.html', context)


@admin_required
def financial_dashboard(request):
    """Dashboard financeiro geral com últimos 30 dias"""
    days = int(request.GET.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    tournaments = Tournament.objects.filter(data__gte=date_from).order_by('-data')
    
    dashboard_data = []
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
        dashboard_data.append({
            'tournament': t,
            'financeiro': fin,
        })
        
        totals['tournaments'] += 1
        totals['players'] += fin['count_players']
        totals['buyin_total'] += fin['buyin_total']
        totals['rake_total'] += fin['rake_total']
        totals['pote_total'] += fin['pote_total']
        totals['premios'] += fin['premios_pagos']
        totals['saldo'] += fin['saldo']
    
    context = {
        'days': days,
        'date_from': date_from,
        'dashboard_data': dashboard_data,
        'totals': totals,
    }
    
    return render(request, 'financial_dashboard.html', context)


@admin_required
def season_financial(request, season_id):
    """Financeiro completo de uma temporada"""
    season = get_object_or_404(Season, id=season_id)
    tournaments = Tournament.objects.filter(season=season).order_by('-data')
    
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
    
    tournaments = Tournament.objects.filter(data__gte=date_from).order_by('data__date')
    
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