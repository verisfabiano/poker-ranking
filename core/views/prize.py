# core/views/prize.py - Views para Sistema de Divisão de Premiação

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from ..models import (
    Tournament, PrizeStructure, PrizePayment, PrizeTemplate, TournamentEntry, Player, TournamentResult
)
from .ranking import tenant_required
from ..decorators.tenant_decorators import admin_required


@admin_required
def prize_distribution_view(request, tournament_id):
    """
    View principal para configurar a distribuição de prêmios de um torneio.
    Mostra opções de modo (Percentual/Fixo) e permite configurar o payout.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    # Verificar se o torneio está em andamento, encerrado ou cancelado (não pode ser agendado)
    if tournament.status == 'AGENDADO':
        return HttpResponseRedirect(
            reverse('tournament_dashboard') + '?error=tournament_not_started'
        )
    
    # Verificar ou criar PrizeStructure
    prize_structure, created = PrizeStructure.objects.get_or_create(
        tournament=tournament,
        defaults={
            'tenant': request.tenant,
            'modo': 'PERCENTUAL',
            'total_prize_pool': tournament.get_prize_pool(),
            'itm_count': tournament.get_recommended_itm_count(),
        }
    )
    
    # Buscar templates disponíveis para o tenant
    templates = PrizeTemplate.objects.filter(
        tenant=request.tenant,
        ativo=True,
        itm_count=prize_structure.itm_count
    ).order_by('nome')
    
    # Buscar jogadores do torneio para seleção posterior
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related('player')
    
    # Buscar resultados do torneio (já com posições informadas)
    results = TournamentResult.objects.filter(tournament=tournament).select_related('player')
    results_by_position = {r.posicao: r for r in results if r.posicao}
    
    # Buscar pagamentos já definidos
    payments = PrizePayment.objects.filter(prize_structure=prize_structure).order_by('position')
    
    # Montar dados de cada posição com jogador + pagamento
    position_data = {}
    for i in range(1, (prize_structure.itm_count or 0) + 1):
        payment = payments.filter(position=i).first()
        result = results_by_position.get(i)
        
        position_data[i] = {
            'player': result.player if result else None,
            'payment': payment,
            'amount': float(payment.amount) if payment and payment.amount else 0.0,
            'percentage': float(payment.percentage) if payment and payment.percentage else None,
        }
    
    # Criar lista de pagamentos com dados de jogador para o template
    payments_with_players = []
    for i in range(1, (prize_structure.itm_count or 0) + 1):
        result = results_by_position.get(i)
        payment = payments.filter(position=i).first()
        if payment:
            payment_data = {
                'position': payment.position,
                'amount': payment.amount,
                'percentage': payment.percentage,
                'player': result.player if result else None,
            }
            payments_with_players.append(payment_data)
    
    context = {
        'tournament': tournament,
        'prize_structure': prize_structure,
        'templates': templates,
        'entries': entries,
        'all_templates': PrizeTemplate.objects.filter(
            tenant=request.tenant,
            ativo=True
        ).values('itm_count').distinct(),
        'position_data': position_data,  # Dados de cada posição com jogador e pagamento
        'payments': payments_with_players,  # Pagamentos com dados de jogador
    }
    
    return render(request, 'prize_distribution.html', context)


@admin_required
@require_POST
def update_prize_config(request, tournament_id):
    """
    AJAX endpoint para atualizar configuração da premiação.
    Pode alterar modo, ITM count, total pool, etc.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(PrizeStructure, tournament=tournament)
    
    if prize_structure.finalizado:
        return JsonResponse({
            'success': False,
            'error': 'Distribuição de prêmios já foi finalizada'
        })
    
    try:
        # Atualizar modo
        modo = request.POST.get('modo', 'PERCENTUAL')
        if modo not in ['PERCENTUAL', 'FIXO']:
            raise ValueError("Modo inválido")
        
        prize_structure.modo = modo
        
        # Atualizar total do pote se fornecido
        total_pool_str = request.POST.get('total_prize_pool', '')
        if total_pool_str:
            total_pool = Decimal(total_pool_str.replace(',', '.'))
            prize_structure.total_prize_pool = total_pool
        
        # Atualizar ITM count
        itm_count_str = request.POST.get('itm_count', '')
        if itm_count_str and itm_count_str.isdigit():
            itm_count = int(itm_count_str)
            prize_structure.itm_count = itm_count
        
        prize_structure.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Configuração atualizada com sucesso',
            'data': {
                'modo': prize_structure.modo,
                'total_pool': str(prize_structure.total_prize_pool),
                'itm_count': prize_structure.itm_count,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@admin_required
@require_POST
def apply_prize_template(request, tournament_id):
    """
    AJAX endpoint para aplicar um template de premiação pré-definido.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(PrizeStructure, tournament=tournament)
    
    try:
        template_id = request.POST.get('template_id')
        if not template_id:
            return JsonResponse({
                'success': False,
                'error': 'Template ID não fornecido'
            })
            
        template = get_object_or_404(PrizeTemplate, id=template_id, tenant=request.tenant)
        
        if not template.data:
            return JsonResponse({
                'success': False,
                'error': 'Template não possui dados configurados'
            })
        
        # Limpar pagamentos anteriores
        prize_structure.payments.all().delete()
        
        # Aplicar template e resetar finalizado para permitir re-edição
        prize_structure.modo = template.modo
        prize_structure.itm_count = template.itm_count
        prize_structure.finalizado = False  # Reset para permitir re-edição
        prize_structure.save()
        
        # Criar PrizePayment para cada posição do template
        for item in template.data:
            position = item.get('position')
            percentage = item.get('percentage')
            valor_fixo = item.get('valor_fixo')
            
            if not position:
                continue
            
            # Calcular amount baseado no modo
            if template.modo == 'PERCENTUAL' and percentage is not None:
                amount = (prize_structure.total_prize_pool * Decimal(str(percentage)) / 100)
            elif valor_fixo is not None:
                amount = Decimal(str(valor_fixo))
            else:
                amount = Decimal('0.00')
            
            PrizePayment.objects.create(
                prize_structure=prize_structure,
                position=position,
                amount=amount,
                percentage=Decimal(str(percentage)) if percentage is not None else None,
                criado_por=request.user,
            )
        
        # Obter os pagamentos atualizados
        payments = list(prize_structure.payments.all().order_by('position').values(
            'position', 'amount', 'percentage'
        ))
        
        # Converter Decimal para float na resposta JSON
        for payment in payments:
            if payment['amount']:
                payment['amount'] = float(payment['amount'])
            if payment['percentage']:
                payment['percentage'] = float(payment['percentage'])
        
        return JsonResponse({
            'success': True,
            'message': f"Template '{template.nome}' aplicado com sucesso",
            'itm_count': template.itm_count,
            'modo': template.modo,
            'payments': payments,
        })
    
    except Exception as e:
        import traceback
        error_msg = f"{str(e)} - {traceback.format_exc()}"
        return JsonResponse({
            'success': False,
            'error': error_msg
        })


@admin_required
@require_POST
def set_prize_payment(request, tournament_id):
    """
    AJAX endpoint para definir o prêmio de uma posição específica.
    Modo: PERCENTUAL - recebe 'percentage'
    Modo: FIXO - recebe 'amount'
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(PrizeStructure, tournament=tournament)
    
    try:
        position = int(request.POST.get('position', 0))
        if position < 1:
            raise ValueError("Posição deve ser >= 1")
        
        # Buscar ou criar PrizePayment
        payment, created = PrizePayment.objects.get_or_create(
            prize_structure=prize_structure,
            position=position,
            defaults={'amount': Decimal('0.00')}
        )
        
        # Atualizar baseado no modo
        if prize_structure.modo == 'PERCENTUAL':
            percentage = request.POST.get('percentage', '')
            if not percentage:
                raise ValueError("Percentual é obrigatório")
            
            percentage = Decimal(percentage.replace(',', '.'))
            if percentage < 0 or percentage > 100:
                raise ValueError("Percentual deve estar entre 0 e 100")
            
            amount = (prize_structure.total_prize_pool * percentage / 100)
            payment.percentage = percentage
            payment.amount = amount
        
        else:  # FIXO
            amount_str = request.POST.get('amount', '')
            if not amount_str:
                raise ValueError("Valor é obrigatório")
            
            amount = Decimal(amount_str.replace(',', '.'))
            payment.amount = amount
            payment.percentage = None
        
        payment.criado_por = request.user
        payment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Prêmio da posição {position} atualizado',
            'data': {
                'position': position,
                'amount': str(payment.amount),
                'percentage': str(payment.percentage) if payment.percentage else None,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@admin_required
@require_POST
def assign_player_to_prize(request, tournament_id):
    """
    AJAX endpoint para vincular um jogador específico a um prêmio.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(PrizeStructure, tournament=tournament)
    
    try:
        position = int(request.POST.get('position', 0))
        player_id = request.POST.get('player_id', '')
        
        payment = get_object_or_404(
            PrizePayment,
            prize_structure=prize_structure,
            position=position
        )
        
        if player_id:
            player = get_object_or_404(
                Player,
                id=player_id,
                tenant=request.tenant
            )
            payment.player = player
        else:
            payment.player = None
        
        payment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Jogador vinculado ao prêmio',
            'data': {
                'position': position,
                'player_name': payment.player.nome if payment.player else None,
                'player_id': payment.player.id if payment.player else None,
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@admin_required
@require_POST
def finalize_prize_distribution(request, tournament_id):
    """
    AJAX endpoint para finalizar a distribuição de prêmios.
    Valida se tudo está preenchido, marca como finalizado, e integra
    as premiações aos resultados dos jogadores baseado na posição informada.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(PrizeStructure, tournament=tournament)
    
    if prize_structure.finalizado:
        return JsonResponse({
            'success': False,
            'error': 'Distribuição de prêmios já foi finalizada'
        })
    
    try:
        # Validar que todas as posições têm valor
        payments = list(prize_structure.payments.all().order_by('position'))
        
        if not payments:
            raise ValueError("Nenhum prêmio foi definido")
        
        for payment in payments:
            if payment.amount <= 0:
                raise ValueError(f"Posição {payment.position} sem valor definido")
        
        # Validar total (com tolerância de arredondamento)
        total_distributed = sum(p.amount for p in payments)
        difference = abs(total_distributed - prize_structure.total_prize_pool)
        
        if difference > Decimal('0.10'):  # Tolerância de 10 centavos
            return JsonResponse({
                'success': False,
                'error': (
                    f"Total distribuído (R$ {total_distributed:.2f}) diferente "
                    f"do pote (R$ {prize_structure.total_prize_pool:.2f})"
                )
            })
        
        # ===== INTEGRAÇÃO: Atribuir premiações aos resultados dos jogadores =====
        # Para cada resultado do torneio, procurar a premiação pela posição
        results = TournamentResult.objects.filter(tournament=tournament)
        updated_count = 0
        
        print(f"[PREMIO] Total de resultados encontrados: {results.count()}")
        
        for result in results:
            print(f"[PREMIO] Verificando resultado - Player: {result.player.nome}, Posição: {result.posicao}")
            
            if result.posicao and result.posicao > 0:
                # Encontrar o pagamento correspondente à posição
                payment = PrizePayment.objects.filter(
                    prize_structure=prize_structure,
                    position=result.posicao
                ).first()
                
                print(f"[PREMIO] Payment encontrado para posição {result.posicao}: {payment}")
                
                if payment:
                    # Atribuir a premiação ao resultado do jogador
                    result.premiacao_recebida = payment.amount
                    result.save()
                    updated_count += 1
                    print(f"[PREMIO] ✅ Premiação atualizada para {result.player.nome}: R$ {payment.amount}")
        
        print(f"[PREMIO] Total de resultados atualizados: {updated_count}")
        
        # Marcar como finalizado
        prize_structure.finalizado = True
        prize_structure.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Distribuição de prêmios finalizada com sucesso! {updated_count} jogadores receberam premiação.',
            'redirect_url': reverse('tournament_dashboard')
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[PREMIO] ❌ ERRO: {str(e)}")
        print(f"[PREMIO] Traceback: {error_trace}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@admin_required
def view_prize_summary(request, tournament_id):
    """
    View para visualizar resumo da distribuição de prêmios (leitura apenas).
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    prize_structure = get_object_or_404(
        PrizeStructure,
        tournament=tournament
    )
    
    payments = PrizePayment.objects.filter(
        prize_structure=prize_structure
    ).select_related('player').order_by('position')
    
    context = {
        'tournament': tournament,
        'prize_structure': prize_structure,
        'payments': payments,
        'total_distributed': sum(p.amount for p in payments),
    }
    
    return render(request, 'prize_summary.html', context)
