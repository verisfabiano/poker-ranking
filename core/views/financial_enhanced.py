"""
Views para novas funcionalidades financeiras:
- Reconciliação automática
- Saldo de caixa em tempo real
- Fluxo de caixa por data
- Relatório financeiro completo
"""

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Q, F
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.models import (
    Tournament, TournamentEntry, TournamentResult, Season, Tenant,
    PlayerProductPurchase, FinancialReconciliation, FinancialLog, User
)
from core.decorators.tenant_decorators import admin_required
from .ranking import tenant_required


def calcular_faturamento_torneio(tournament):
    """
    Calcula faturamento completo e esperado de um torneio.
    Considera apenas produtos que entram em premiação (Add-on, Rebuy).
    RAKE é calculado sobre TUDO: buy-in + rebuys + add-ons + produtos.
    """
    entries = TournamentEntry.objects.filter(tournament=tournament, confirmado_pelo_admin=True)
    results = TournamentResult.objects.filter(tournament=tournament)
    
    count_players = entries.count()
    # Count rebuys e addons from PlayerProductPurchase (filterng by product name)
    count_rebuys = PlayerProductPurchase.objects.filter(
        tournament=tournament, 
        product__nome__icontains='rebuy'
    ).aggregate(total=Count('id'))['total'] or 0
    count_addons = PlayerProductPurchase.objects.filter(
        tournament=tournament, 
        product__nome__icontains='addon'
    ).aggregate(total=Count('id'))['total'] or 0
    
    # FATURAMENTO BRUTO (TOTAL ARRECADADO)
    faturamento_bruto = Decimal('0')
    
    # Buy-ins
    if tournament.buyin:
        total_buyin = count_players * Decimal(str(tournament.buyin))
        faturamento_bruto += total_buyin
    
    # Rebuys
    if tournament.permite_rebuy and count_rebuys > 0 and tournament.rebuy_valor:
        total_rebuys = count_rebuys * Decimal(str(tournament.rebuy_valor))
        faturamento_bruto += total_rebuys
    
    # Add-ons
    if tournament.permite_addon and count_addons > 0 and tournament.addon_valor:
        total_addons = count_addons * Decimal(str(tournament.addon_valor))
        faturamento_bruto += total_addons
    
    # Produtos que ENTRAM em premiação (apenas Add-on, Rebuy, etc - não Jack Pot, Staff, etc)
    total_produtos = PlayerProductPurchase.objects.filter(
        tournament=tournament,
        product__entra_em_premiacao=True
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    faturamento_bruto += total_produtos
    
    # RAKE ESPERADO - Calculado sobre TUDO (faturamento bruto)
    rake_esperado = Decimal('0')
    
    # Usar a configuração geral do torneio (rake_type e rake_percentual/rake_valor)
    if tournament.rake_type in ['FIXO', 'MISTO']:
        # Rake fixo por jogador no buy-in
        rake_esperado += count_players * Decimal(str(tournament.rake_valor or 0))
    if tournament.rake_type in ['PERCENTUAL', 'MISTO']:
        # Rake percentual sobre o TOTAL arrecadado
        rake_esperado += faturamento_bruto * (Decimal(str(tournament.rake_percentual or 0)) / Decimal('100'))
    
    # Produtos que NÃO entram em premiação (Jack Pot, Staff, Bounty, etc) - apenas informativos
    total_outros_produtos = PlayerProductPurchase.objects.filter(
        tournament=tournament,
        product__entra_em_premiacao=False
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or Decimal('0')
    
    # FATURAMENTO REAL (o que foi registrado)
    premios_pagos = results.aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or Decimal('0')
    
    # Prize pool esperado
    prize_pool_esperado = faturamento_bruto - rake_esperado
    
    return {
        'count_players': count_players,
        'count_rebuys': count_rebuys,
        'count_addons': count_addons,
        'faturamento_bruto_esperado': faturamento_bruto,
        'rake_esperado': rake_esperado,
        'prize_pool_esperado': prize_pool_esperado,
        'produtos_premiacao': total_produtos,
        'outros_produtos': total_outros_produtos,
        'premios_pagos': premios_pagos,
        'saldo': prize_pool_esperado - premios_pagos,
    }


@admin_required
@require_http_methods(["POST"])
def reconciliar_torneio(request, tournament_id):
    """
    Reconcilia um torneio e detecta discrepâncias.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    financeiro = calcular_faturamento_torneio(tournament)
    
    # Criar ou atualizar reconciliação
    reconciliation, created = FinancialReconciliation.objects.get_or_create(
        tournament=tournament,
        defaults={'tenant': request.tenant}
    )
    
    # Atualizar valores
    reconciliation.faturamento_esperado = financeiro['faturamento_bruto_esperado']
    reconciliation.rake_esperado = financeiro['rake_esperado']
    reconciliation.premio_pool_esperado = financeiro['prize_pool_esperado']
    reconciliation.faturamento_real = financeiro['faturamento_bruto_esperado']  # Assumir que foi tudo recebido
    reconciliation.premios_pagos = financeiro['premios_pagos']
    reconciliation.reconciliado_por = request.user
    
    # Calcular discrepância
    reconciliation.calcular_diferenca()
    
    # Adicionar observação do usuário se fornecida
    if 'observacao' in request.POST:
        reconciliation.observacao = request.POST.get('observacao', '')
    
    reconciliation.save()
    
    return redirect('tournament_financial', tournament_id=tournament_id)


@admin_required
def saldo_caixa_diario(request):
    """
    Dashboard de saldo de caixa diário com fluxo.
    Mostra dia-a-dia: entradas, saídas, saldo.
    """
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    date_to = timezone.now().date()
    
    # Pegar todos os torneios do período
    tournaments = Tournament.objects.filter(
        tenant=request.tenant,
        data__date__gte=date_from,
        data__date__lte=date_to
    ).order_by('data')
    
    # Agrupar por data
    daily_cash_flow = {}
    running_balance = Decimal('0')
    
    for day in (date_from + timedelta(n) for n in range((date_to - date_from).days + 1)):
        day_tournaments = tournaments.filter(data__date=day)
        
        day_data = {
            'date': day,
            'tournaments': [],
            'total_entrada': Decimal('0'),
            'total_saida': Decimal('0'),
            'saldo_dia': Decimal('0'),
            'saldo_acumulado': Decimal('0'),
        }
        
        for t in day_tournaments:
            financeiro = calcular_faturamento_torneio(t)
            
            entrada = financeiro['faturamento_bruto_esperado']
            saida = financeiro['rake_esperado'] + financeiro['premios_pagos']
            saldo = entrada - saida
            
            day_data['tournaments'].append({
                'tournament': t,
                'entrada': entrada,
                'saida': saida,
                'saldo': saldo,
            })
            
            day_data['total_entrada'] += entrada
            day_data['total_saida'] += saida
        
        day_data['saldo_dia'] = day_data['total_entrada'] - day_data['total_saida']
        running_balance += day_data['saldo_dia']
        day_data['saldo_acumulado'] = running_balance
        
        if day_data['tournaments']:  # Só adicionar dias com atividade
            daily_cash_flow[day.isoformat()] = day_data
    
    context = {
        'days': days,
        'date_from': date_from,
        'date_to': date_to,
        'daily_cash_flow': daily_cash_flow,
        'saldo_final': running_balance,
    }
    
    return render(request, 'financial_cash_flow_daily.html', context)


@admin_required
def relatorio_financeiro_completo(request):
    """
    Relatório financeiro completo com comparativas.
    """
    # Período atual
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
    
    # Período anterior (para comparação)
    days_diff = (end_date - start_date).days
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=days_diff)
    
    # Dados período atual
    tournaments_current = Tournament.objects.filter(
        tenant=request.tenant,
        data__date__gte=start_date,
        data__date__lte=end_date
    )
    
    # Dados período anterior
    tournaments_previous = Tournament.objects.filter(
        tenant=request.tenant,
        data__date__gte=prev_start_date,
        data__date__lte=prev_end_date
    )
    
    def calcular_totais(tournaments):
        totals = {
            'num_torneios': tournaments.count(),
            'num_jogadores': 0,
            'faturamento_bruto': Decimal('0'),
            'rake_total': Decimal('0'),
            'prize_pool_total': Decimal('0'),
            'premios_pagos': Decimal('0'),
            'saldo': Decimal('0'),
            'margem_percentual': Decimal('0'),
        }
        
        for t in tournaments:
            financeiro = calcular_faturamento_torneio(t)
            totals['num_jogadores'] += financeiro['count_players']
            totals['faturamento_bruto'] += financeiro['faturamento_bruto_esperado']
            totals['rake_total'] += financeiro['rake_esperado']
            totals['prize_pool_total'] += financeiro['prize_pool_esperado']
            totals['premios_pagos'] += financeiro['premios_pagos']
        
        totals['saldo'] = totals['faturamento_bruto'] - totals['rake_total'] - totals['premios_pagos']
        
        if totals['faturamento_bruto'] > 0:
            totals['margem_percentual'] = (totals['rake_total'] / totals['faturamento_bruto']) * Decimal('100')
        
        return totals
    
    totals_current = calcular_totais(tournaments_current)
    totals_previous = calcular_totais(tournaments_previous)
    
    # Enriquecer tournaments_current com dados financeiros
    tournaments_current_data = []
    for t in tournaments_current:
        fin = calcular_faturamento_torneio(t)
        t.financeiro = fin  # Adicionar como atributo do objeto
        tournaments_current_data.append(t)
    
    # Calcular variação
    variacao = {
        'torneios_pct': Decimal('0'),
        'jogadores_pct': Decimal('0'),
        'faturamento_pct': Decimal('0'),
        'margem_pct': Decimal('0'),
    }
    
    if totals_previous['num_torneios'] > 0:
        variacao['torneios_pct'] = ((totals_current['num_torneios'] - totals_previous['num_torneios']) / totals_previous['num_torneios']) * Decimal('100')
    if totals_previous['num_jogadores'] > 0:
        variacao['jogadores_pct'] = ((totals_current['num_jogadores'] - totals_previous['num_jogadores']) / totals_previous['num_jogadores']) * Decimal('100')
    if totals_previous['faturamento_bruto'] > 0:
        variacao['faturamento_pct'] = ((totals_current['faturamento_bruto'] - totals_previous['faturamento_bruto']) / totals_previous['faturamento_bruto']) * Decimal('100')
    if totals_previous['margem_percentual'] > 0:
        variacao['margem_pct'] = totals_current['margem_percentual'] - totals_previous['margem_percentual']
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'start_date_str': start_date_str,
        'end_date_str': end_date_str,
        'tournaments_current': tournaments_current_data,
        'totals_current': totals_current,
        'totals_previous': totals_previous,
        'variacao': variacao,
    }
    
    return render(request, 'financial_relatorio_completo.html', context)


@admin_required
def api_financial_reconciliation(request):
    """
    API JSON com status de reconciliação de todos os torneios.
    """
    tournaments = Tournament.objects.filter(
        tenant=request.tenant
    ).select_related('reconciliation')
    
    data = []
    for t in tournaments:
        try:
            recon = t.reconciliation
            status = recon.status
            diferenca = float(recon.diferenca)
        except FinancialReconciliation.DoesNotExist:
            status = 'PENDING'
            diferenca = 0
        
        data.append({
            'tournament_id': t.id,
            'tournament_name': t.nome,
            'date': t.data.isoformat(),
            'status': status,
            'diferenca': diferenca,
        })
    
    return JsonResponse({'tournaments': data})
