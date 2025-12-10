from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from ..models import Tournament
from .auth import admin_required

@admin_required
def director_panel(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
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
    t = get_object_or_404(Tournament, id=tournament_id)
    
    if not t.blind_structure:
        messages.error(request, "Este torneio não tem estrutura de blinds definida.")
        return redirect("director_panel", tournament_id=t.id)

    now = timezone.now()
    level = t.get_current_blind()
    total_seconds = level.tempo_minutos * 60 if level else 0

    if t.is_paused:
        # --- RESUMAR (Dar Play) ---
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
    t = get_object_or_404(Tournament, id=tournament_id)
    
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