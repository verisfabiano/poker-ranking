from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Tournament
from .auth import admin_required 
# Nota: Podemos remover o admin_required depois se quisermos que o telão seja público, 
# mas por enquanto vamos proteger.

def api_tournament_status(request, tournament_id):
    t = get_object_or_404(Tournament, id=tournament_id)
    
    # 1. Dados básicos
    data = {
        "status": t.status,
        "is_paused": t.is_paused,
        "active_tables": t.active_tables,
        "players_count": t.entries.count(),
    }

    # 2. Dados do Nível Atual (Blinds)
    current_level = t.get_current_blind()
    if current_level:
        data["level"] = {
            "ordem": current_level.ordem,
            "small_blind": current_level.small_blind,
            "big_blind": current_level.big_blind,
            "ante": current_level.ante,
            "is_break": current_level.is_break,
            "tempo_total": current_level.tempo_minutos * 60, # convertendo para segundos
        }
    else:
        data["level"] = None

    # 3. Cálculo do Tempo Restante (A Mágica)
    # Se estiver PAUSADO, usamos o tempo que foi salvo quando pausou.
    if t.is_paused:
        remaining = t.seconds_remaining_at_pause or 0
    else:
        # Se estiver RODANDO, calculamos: 
        # (Tempo Total do Nível) - (Tempo que já passou desde que demos play)
        if t.last_level_start and current_level:
            now = timezone.now()
            # Quanto tempo passou desde o último "Play"?
            elapsed = (now - t.last_level_start).total_seconds()
            
            # Quanto tempo tínhamos no relógio quando demos play?
            # Se seconds_remaining_at_pause for None, era o nível inteiro.
            initial_seconds = t.seconds_remaining_at_pause
            if initial_seconds is None:
                initial_seconds = current_level.tempo_minutos * 60
            
            remaining = initial_seconds - elapsed
        else:
            remaining = 0

    # Garantir que não dê número negativo
    data["remaining_seconds"] = max(0, int(remaining))

    return JsonResponse(data)