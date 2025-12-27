from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from ..models import Tournament
from ..decorators.tenant_decorators import admin_required
from .ranking import tenant_required

@admin_required
def director_panel(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    current_blind = tournament.get_current_blind()
    
    context = {
        "tournament": tournament,
        "blind": current_blind,
        "next_blind": tournament.blind_structure.levels.filter(ordem=tournament.current_level_order + 1).first() if tournament.blind_structure else None
    }
    return render(request, "director_panel.html", context)

@admin_required
def director_toggle_timer(request, tournament_id):
    """Lógica de Play/Pause"""
    t = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    if not t.blind_structure:
        messages.error(request, "Este torneio não tem estrutura de blinds definida.")
        return redirect("director_panel", tournament_id=t.id)

    now = timezone.now()
    level = t.get_current_blind()
    total_seconds = level.tempo_minutos * 60 if level else 0

    if t.is_paused:
        # --- RESUMAR (Dar Play) ---
        # Se o torneio ainda não foi iniciado, marcar como EM_ANDAMENTO
        if t.status == "AGENDADO":
            t.status = "EM_ANDAMENTO"
        
        # Se não tem segundos salvos (primeiro play), assume tempo total
        if t.seconds_remaining_at_pause is None:
            t.seconds_remaining_at_pause = total_seconds
            
        t.is_paused = False
        t.last_level_start = now
        # O truque: definimos o start no passado para bater com o tempo restante
        # Ex: Faltam 10min (600s). Nível é 20min (1200s).
        # Significa que já passaram 600s.
        # last_level_start = now - (total - restante)
        elapsed = total_seconds - t.seconds_remaining_at_pause
        t.last_level_start = now - timezone.timedelta(seconds=elapsed)
    else:
        # --- PAUSAR ---
        t.is_paused = True
        # Calcular quanto tempo sobrou agora
        if t.last_level_start:
            elapsed = (now - t.last_level_start).total_seconds()
            remaining = total_seconds - elapsed
            t.seconds_remaining_at_pause = max(0, int(remaining))
        else:
            t.seconds_remaining_at_pause = total_seconds # Caso de fallback

    t.save()
    return redirect("director_panel", tournament_id=t.id)

@admin_required
def director_change_level(request, tournament_id, direction):
    """Mudar nível (prev/next)"""
    t = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    if not t.blind_structure:
        return redirect("director_panel", tournament_id=t.id)

    max_levels = t.blind_structure.levels.count()
    
    if direction == 'next':
        if t.current_level_order < max_levels:
            t.current_level_order += 1
            # Resetar timer para o novo nível
            t.is_paused = True
            new_level = t.get_current_blind()
            t.seconds_remaining_at_pause = new_level.tempo_minutos * 60
            t.last_level_start = None
            
    elif direction == 'prev':
        if t.current_level_order > 1:
            t.current_level_order -= 1
            # Resetar timer
            t.is_paused = True
            new_level = t.get_current_blind()
            t.seconds_remaining_at_pause = new_level.tempo_minutos * 60
            t.last_level_start = None

    t.save()
    return redirect("director_panel", tournament_id=t.id)

def tv_dashboard(request, tournament_id):
    t = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    return render(request, "tv_dashboard.html", {"tournament": t})


def tournament_status_api(request, tournament_id):
    """API que retorna status do torneio em JSON para a TV - Sem autenticação de tenant"""
    import sys
    from django.utils import timezone
    from ..models import PrizeStructure
    
    # Buscar o torneio sem validação de tenant (a TV não tem contexto de sessão)
    t = get_object_or_404(Tournament, id=tournament_id)
    blind = t.get_current_blind()
    next_blind = t.blind_structure.levels.filter(ordem=t.current_level_order + 1).first() if t.blind_structure else None
    
    # Calcular tempo restante CORRETAMENTE
    if blind:
        level_duration = blind.tempo_minutos * 60  # em segundos
        
        if t.is_paused:
            remaining_seconds = t.seconds_remaining_at_pause if t.seconds_remaining_at_pause is not None else level_duration
        else:
            # Se está rodando, calcular quanto tempo ainda falta
            if t.last_level_start:
                elapsed = (timezone.now() - t.last_level_start).total_seconds()
                remaining_seconds = level_duration - elapsed
            else:
                remaining_seconds = level_duration
            
            # Garantir que não fica negativo
            remaining_seconds = max(0, int(remaining_seconds))
    else:
        remaining_seconds = 0
    
    # Dados de premiação
    prize_data = None
    try:
        prize_structure = PrizeStructure.objects.filter(tournament=t).first()
        if prize_structure:
            payments = prize_structure.payments.all()
            itm_count = payments.count()
            total_prize = sum(float(p.amount) for p in payments)
            
            prize_data = {
                "itm_count": itm_count,
                "total_prize": total_prize,
                "configured": True,
                "payments": [
                    {
                        "position": p.posicao,
                        "amount": float(p.amount),
                        "player_name": p.player.nome if p.player else "Indefinido"
                    }
                    for p in payments.order_by('posicao')[:15]  # Top 15 apenas
                ]
            }
        else:
            prize_data = {"configured": False, "itm_count": 0, "total_prize": 0}
    except:
        prize_data = {"configured": False, "itm_count": 0, "total_prize": 0}
    
    # Calcular tempo até próximo intervalo
    time_to_next_break = None
    if t.blind_structure and blind:
        time_accumulated = remaining_seconds  # Tempo restante do nível atual
        
        # Procurar pelo próximo intervalo
        all_levels = t.blind_structure.levels.all().order_by('ordem')
        next_is_break = False
        
        for level in all_levels:
            if level.ordem > blind.ordem:
                time_accumulated += level.tempo_minutos * 60
                if level.is_break:
                    time_to_next_break = int(time_accumulated / 60)  # Converter para minutos
                    next_is_break = True
                    break
        
        # Se não encontrou intervalo, tentar do começo (caso tenha múltiplos ciclos)
        if not next_is_break:
            for level in all_levels:
                if level.is_break:
                    time_to_next_break = int(time_accumulated / 60)
                    break
    
    return JsonResponse({
        "tournament_id": t.id,
        "tournament_name": t.nome,
        "status": t.status,
        "is_paused": t.is_paused,
        "level": {
            "ordem": blind.ordem if blind else 1,
            "is_break": blind.is_break if blind else False,
            "small_blind": blind.small_blind if blind and not blind.is_break else 0,
            "big_blind": blind.big_blind if blind and not blind.is_break else 0,
            "ante": blind.ante if blind and not blind.is_break else 0,
            "tempo_minutos": blind.tempo_minutos if blind else 0,
        },
        "next_level": {
            "ordem": next_blind.ordem if next_blind else None,
            "is_break": next_blind.is_break if next_blind else False,
            "small_blind": next_blind.small_blind if next_blind and not next_blind.is_break else 0,
            "big_blind": next_blind.big_blind if next_blind and not next_blind.is_break else 0,
            "tempo_minutos": next_blind.tempo_minutos if next_blind else 0,
        } if next_blind else None,
        "players_count": t.get_active_players_count(),
        "active_tables": t.get_active_tables_count(),
        "average_stack": int(t.get_average_stack()),
        "remaining_seconds": remaining_seconds,
        "time_to_next_break": time_to_next_break,
        "prize": prize_data,
    })


def tournament_update_status(request, tournament_id):
    """API para atualizar o status do torneio (AGENDADO, EM_ANDAMENTO, FINALIZADO, CANCELADO)"""
    import json
    
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=400)
    
    try:
        data = json.loads(request.body)
        novo_status = data.get('status')
        
        # Validar status
        status_validos = ['AGENDADO', 'EM_ANDAMENTO', 'FINALIZADO', 'CANCELADO']
        if novo_status not in status_validos:
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
        
        # Validar transições de status
        status_atual = tournament.status
        
        # Permitir transições lógicas
        transicoes_permitidas = {
            'AGENDADO': ['EM_ANDAMENTO', 'CANCELADO'],
            'EM_ANDAMENTO': ['FINALIZADO', 'CANCELADO'],
            'FINALIZADO': ['CANCELADO'],
            'CANCELADO': []
        }
        
        if novo_status not in transicoes_permitidas.get(status_atual, []):
            return JsonResponse({
                'success': False, 
                'error': f'Não é possível mudar de {status_atual} para {novo_status}'
            }, status=400)
        
        # Atualizar status
        tournament.status = novo_status
        tournament.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status alterado para {novo_status.replace("_", " ").title()}',
            'novo_status': novo_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Alias para compatibilidade com urls.py
api_tournament_status = tournament_status_api