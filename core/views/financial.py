from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, F
from core.models import Tournament, TournamentEntry
from .auth import admin_required

@admin_required
def tournament_financial(request, tournament_id):
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
                # Adiciona mais um addon (se o clube permitir múltiplos, senão limitar no template)
                entry.qtde_addons += 1
                entry.valor_total_pago += t.addon_cost
                messages.success(request, f"Add-on adicionado para {entry.player.apelido or entry.player.nome}")
            
            elif action == 'toggle_timechip':
                # Alternar Time Chip (Staff Bonus)
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
    
    # Contagens
    count_buyins = entries.count() # Todos inscritos pagam buyin
    count_rebuys = entries.aggregate(s=Sum('qtde_rebuys'))['s'] or 0
    count_addons = entries.aggregate(s=Sum('qtde_addons'))['s'] or 0
    count_timechip = entries.filter(usou_time_chip=True).count()

    # Valores Monetários Totais
    # 1. Buy-ins (Valor Pote + Rake Fixo)
    total_buyin_pote = count_buyins * t.buy_in
    total_rake_fixo = count_buyins * t.rake
    
    # 2. Rebuys e Addons
    total_rebuy = count_rebuys * t.rebuy_cost
    total_addon = count_addons * t.addon_cost
    total_timechip = count_timechip * t.time_chip_cost

    # Arrecadação Bruta (Tudo que entrou no caixa)
    gross_total = (count_buyins * (t.buy_in + t.rake)) + total_rebuy + total_addon + total_timechip

    # Cálculo do que fica pra casa (Rake) e o que vai pros jogadores (Prize Pool)
    # A. Rake Fixo (Taxa de inscrição)
    # B. Rake Porcentagem (Se houver config de % sobre rebuys/addons ou total)
    # Geralmente Time Chip vai 100% pra Staff (Casa)
    
    rake_total = total_rake_fixo + total_timechip 
    
    # Se tiver porcentagem definida no torneio sobre o pote
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