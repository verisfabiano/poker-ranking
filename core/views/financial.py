# core/views/financial.py - VERSÃO EXPANDIDA COMPLETA

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from core.models import Tournament, TournamentEntry, Season
from .auth import admin_required


# ============================================================
#  VIEW FINANCEIRO POR TORNEIO (JÁ EXISTENTE - AQUI PARA CONTEXTO)
# ============================================================

@admin_required
def tournament_financial(request, tournament_id):
    """Gerenciar financeiro e rebuys/addons de um torneio específico"""
    t = get_object_or_404(Tournament, id=tournament_id)
    
    # Processamento de Formulário (POST)
    if request.method == "POST":
        entry_id = request.POST.get('entry_id')
        action = request.POST.get('action')
        entry = get_object_or_404(TournamentEntry, id=entry_id, tournament=t)
        
        try:
            if action == 'rebuy':
                entry.qtde_rebuys += 1
                entry.valor_total_pago += t.rebuy_cost
                messages.success(request, f"Rebuy adicionado para {entry.player.apelido or entry.player.nome}")
                
            elif action == 'addon':
                entry.qtde_addons += 1
                entry.valor_total_pago += t.addon_cost
                messages.success(request, f"Add-on adicionado para {entry.player.apelido or entry.player.nome}")
            
            elif action == 'toggle_timechip':
                if entry.usou_time_chip:
                    entry.usou_time_chip = False
                    entry.valor_total_pago -= t.time_chip_cost
                else:
                    entry.usou_time_chip = True
                    entry.valor_total_pago += t.time_chip_cost
                messages.info(request, f"Status Time Chip alterado para {entry.player.nome}")

            entry.save()
            
        except Exception as e:
            messages.error(request, f"Erro ao salvar: {e}")
            
        return redirect('tournament_financial', tournament_id=t.id)

    # --- CÁLCULOS DO DASHBOARD ---
    entries = TournamentEntry.objects.filter(tournament=t).select_related('player').order_by('player__nome')
    
    count_buyins = entries.count()
    count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
    count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
    count_timechip = entries.filter(usou_time_chip=True).count()

    total_buyin_pote = count_buyins * t.buy_in
    total_rake_fixo = count_buyins * t.rake
    total_rebuy = count_rebuys * t.rebuy_cost
    total_addon = count_addons * t.addon_cost
    total_timechip = count_timechip * t.time_chip_cost

    gross_total = (count_buyins * (t.buy_in + t.rake)) + total_rebuy + total_addon + total_timechip

    rake_total = total_rake_fixo + total_timechip
    pot_gross = total_buyin_pote + total_rebuy + total_addon
    rake_percent_val = pot_gross * (t.percentage_rake / 100)
    rake_total += rake_percent_val

    prize_pool = gross_total - rake_total

    context = {
        't': t,
        'entries': entries,
        'financial': {
            'gross_total': gross_total,
            'prize_pool': prize_pool,
            'rake_total': rake_total,
            'count_buyins': count_buyins,
            'count_rebuys': count_rebuys,
            'count_addons': count_addons,
            'count_timechip': count_timechip,
        }
    }
    
    return render(request, 'tournament_financial.html', context)


# ============================================================
#  PAINEL FINANCEIRO GERAL
# ============================================================

@admin_required
def financial_dashboard(request):
    """
    Dashboard financeiro geral com resumo de todas as temporadas.
    Mostra totais de movimentação, rake e premio pool.
    """
    # Período selecionado (padrão: últimos 30 dias)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    tournaments = Tournament.objects.filter(data__gte=date_from).select_related('season')
    
    # TOTALIZAÇÕES GERAIS
    total_tournaments = tournaments.count()
    total_players_by_tournament = TournamentEntry.objects.filter(
        tournament__in=tournaments
    ).values('tournament').annotate(count=Count('id'))
    
    # Cálculos financeiros
    financial_data = []
    grand_total_gross = Decimal('0.00')
    grand_total_rake = Decimal('0.00')
    grand_total_prize = Decimal('0.00')
    
    for t in tournaments:
        entries = TournamentEntry.objects.filter(tournament=t)
        
        count_buyins = entries.count()
        count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
        count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
        count_timechip = entries.filter(usou_time_chip=True).count()

        total_buyin_pote = Decimal(count_buyins) * t.buy_in
        total_rake_fixo = Decimal(count_buyins) * t.rake
        total_rebuy = Decimal(count_rebuys) * t.rebuy_cost
        total_addon = Decimal(count_addons) * t.addon_cost
        total_timechip = Decimal(count_timechip) * t.time_chip_cost

        gross_total = (Decimal(count_buyins) * (t.buy_in + t.rake)) + total_rebuy + total_addon + total_timechip

        rake_total = total_rake_fixo + total_timechip
        pot_gross = total_buyin_pote + total_rebuy + total_addon
        rake_percent_val = pot_gross * (Decimal(t.percentage_rake) / 100)
        rake_total += rake_percent_val

        prize_pool = gross_total - rake_total
        
        financial_data.append({
            'tournament': t,
            'count_players': count_buyins,
            'gross_total': gross_total,
            'rake_total': rake_total,
            'prize_pool': prize_pool,
            'rebuys': count_rebuys,
            'addons': count_addons,
        })
        
        grand_total_gross += gross_total
        grand_total_rake += rake_total
        grand_total_prize += prize_pool
    
    # Ordenar por data (mais recentes primeiro)
    financial_data.sort(key=lambda x: x['tournament'].data, reverse=True)
    
    context = {
        'days': days,
        'date_from': date_from,
        'total_tournaments': total_tournaments,
        'financial_data': financial_data,
        'grand_total_gross': grand_total_gross,
        'grand_total_rake': grand_total_rake,
        'grand_total_prize': grand_total_prize,
    }
    
    return render(request, 'financial_dashboard.html', context)


# ============================================================
#  FINANCEIRO POR TEMPORADA
# ============================================================

@admin_required
def season_financial(request, season_id):
    """
    Financeiro completo de uma temporada específica.
    Mostra todos os torneios da temporada com detalhes financeiros.
    """
    season = get_object_or_404(Season, id=season_id)
    tournaments = Tournament.objects.filter(season=season).order_by('-data')
    
    financial_data = []
    season_total_gross = Decimal('0.00')
    season_total_rake = Decimal('0.00')
    season_total_prize = Decimal('0.00')
    
    for t in tournaments:
        entries = TournamentEntry.objects.filter(tournament=t)
        
        count_buyins = entries.count()
        count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
        count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
        count_timechip = entries.filter(usou_time_chip=True).count()

        total_buyin_pote = Decimal(count_buyins) * t.buy_in
        total_rake_fixo = Decimal(count_buyins) * t.rake
        total_rebuy = Decimal(count_rebuys) * t.rebuy_cost
        total_addon = Decimal(count_addons) * t.addon_cost
        total_timechip = Decimal(count_timechip) * t.time_chip_cost

        gross_total = (Decimal(count_buyins) * (t.buy_in + t.rake)) + total_rebuy + total_addon + total_timechip

        rake_total = total_rake_fixo + total_timechip
        pot_gross = total_buyin_pote + total_rebuy + total_addon
        rake_percent_val = pot_gross * (Decimal(t.percentage_rake) / 100)
        rake_total += rake_percent_val

        prize_pool = gross_total - rake_total
        
        financial_data.append({
            'tournament': t,
            'count_players': count_buyins,
            'gross_total': gross_total,
            'rake_total': rake_total,
            'prize_pool': prize_pool,
            'details': {
                'rebuys': count_rebuys,
                'addons': count_addons,
                'timechips': count_timechip,
            }
        })
        
        season_total_gross += gross_total
        season_total_rake += rake_total
        season_total_prize += prize_pool
    
    context = {
        'season': season,
        'financial_data': financial_data,
        'season_total_gross': season_total_gross,
        'season_total_rake': season_total_rake,
        'season_total_prize': season_total_prize,
        'tournament_count': len(financial_data),
    }
    
    return render(request, 'season_financial.html', context)


# ============================================================
#  FINANCEIRO POR PERÍODO (CUSTOM DATE RANGE)
# ============================================================

@admin_required
def financial_by_period(request):
    """
    Financeiro por período customizável.
    Permite filtrar por data inicial e final.
    """
    # Parâmetros de filtro
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    # Se não tiver datas, usar padrão (últimos 30 dias)
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
    
    # Filtrar torneios por período
    tournaments = Tournament.objects.filter(
        data__date__gte=start_date,
        data__date__lte=end_date
    ).order_by('-data')
    
    # Agrupar por data para visualização
    daily_financial = {}
    period_total_gross = Decimal('0.00')
    period_total_rake = Decimal('0.00')
    period_total_prize = Decimal('0.00')
    
    for t in tournaments:
        date_key = t.data.date()
        
        entries = TournamentEntry.objects.filter(tournament=t)
        count_buyins = entries.count()
        count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
        count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
        count_timechip = entries.filter(usou_time_chip=True).count()

        total_buyin_pote = Decimal(count_buyins) * t.buy_in
        total_rake_fixo = Decimal(count_buyins) * t.rake
        total_rebuy = Decimal(count_rebuys) * t.rebuy_cost
        total_addon = Decimal(count_addons) * t.addon_cost
        total_timechip = Decimal(count_timechip) * t.time_chip_cost

        gross_total = (Decimal(count_buyins) * (t.buy_in + t.rake)) + total_rebuy + total_addon + total_timechip

        rake_total = total_rake_fixo + total_timechip
        pot_gross = total_buyin_pote + total_rebuy + total_addon
        rake_percent_val = pot_gross * (Decimal(t.percentage_rake) / 100)
        rake_total += rake_percent_val

        prize_pool = gross_total - rake_total
        
        if date_key not in daily_financial:
            daily_financial[date_key] = {
                'tournaments': [],
                'total_gross': Decimal('0.00'),
                'total_rake': Decimal('0.00'),
                'total_prize': Decimal('0.00'),
            }
        
        daily_financial[date_key]['tournaments'].append({
            'tournament': t,
            'count_players': count_buyins,
            'gross_total': gross_total,
            'rake_total': rake_total,
            'prize_pool': prize_pool,
        })
        
        daily_financial[date_key]['total_gross'] += gross_total
        daily_financial[date_key]['total_rake'] += rake_total
        daily_financial[date_key]['total_prize'] += prize_pool
        
        period_total_gross += gross_total
        period_total_rake += rake_total
        period_total_prize += prize_pool
    
    # Ordenar datas
    daily_financial = dict(sorted(daily_financial.items(), reverse=True))
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'start_date_str': start_date_str,
        'end_date_str': end_date_str,
        'daily_financial': daily_financial,
        'period_total_gross': period_total_gross,
        'period_total_rake': period_total_rake,
        'period_total_prize': period_total_prize,
        'tournament_count': tournaments.count(),
    }
    
    return render(request, 'financial_by_period.html', context)


# ============================================================
#  API JSON PARA GRÁFICOS / DASHBOARDS AVANÇADOS
# ============================================================

@admin_required
def api_financial_summary(request):
    """
    Retorna JSON com resumo financeiro para construir gráficos.
    Params: days=30 (padrão)
    """
    days = int(request.GET.get('days', 30))
    date_from = timezone.now() - timedelta(days=days)
    
    tournaments = Tournament.objects.filter(data__gte=date_from)
    
    # Agregações por dia
    daily_data = {}
    for t in tournaments:
        date_key = t.data.date().isoformat()
        
        entries = TournamentEntry.objects.filter(tournament=t)
        count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
        count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
        
        gross = (entries.count() * (t.buy_in + t.rake)) + \
                (count_rebuys * t.rebuy_cost) + \
                (count_addons * t.addon_cost)
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                'tournaments': 0,
                'players': 0,
                'gross': 0,
            }
        
        daily_data[date_key]['tournaments'] += 1
        daily_data[date_key]['players'] += entries.count()
        daily_data[date_key]['gross'] += float(gross)
    
    return JsonResponse({
        'days': days,
        'daily_data': daily_data,
        'total_days': len(daily_data),
    })