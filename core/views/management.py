# core/views/management.py

from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse

from ..models import (
    Season, Tournament, TournamentType, BlindStructure, 
    TournamentEntry, TournamentResult
)
from ..decorators.tenant_decorators import admin_required
from .ranking import tenant_required


# ============================================================
#  GERENCIAMENTO DE BLIND STRUCTURES
# ============================================================

@admin_required
def blind_structure_manage(request, structure_id):
    """Gerenciar níveis de blinds de uma estrutura"""
    structure = get_object_or_404(BlindStructure, id=structure_id)
    
    if request.method == "POST":
        # Processar adicionar/remover níveis
        # (implementar conforme necessário)
        pass
    
    return render(request, "blind_structure_manage.html", {
        "structure": structure,
    })


# ============================================================
#  LANÇAMENTO DE RESULTADOS
# ============================================================

@admin_required
def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    season = tournament.season
    mensagem = None
    mensagem_erro = None
    dados_post = {}
    
    if request.method == "POST":
        entries = TournamentEntry.objects.filter(tournament=tournament)
        posicoes_digitadas = {}
        
        # Armazenar TODOS os dados do POST primeiro
        for entry in entries:
            pid = entry.player.id
            pos_str = request.POST.get(f"pos_{pid}", "").strip()
            ajuste_str = request.POST.get(f"ajuste_{pid}", "").strip()
            prize_str = request.POST.get(f"prize_{pid}", "").replace(",", ".").strip()
            
            dados_post[pid] = {
                'pos': pos_str,
                'ajuste': ajuste_str,
                'prize': prize_str,
            }
        
        # Validar posições duplicadas
        for entry in entries:
            pid = entry.player.id
            pos_str = dados_post[pid]['pos']
            
            if pos_str:
                try:
                    pos_int = int(pos_str)
                    if pos_int in posicoes_digitadas:
                        mensagem_erro = f"❌ Posição {pos_int} foi atribuída a {posicoes_digitadas[pos_int]} e {entry.player.nome}! Corrija antes de salvar."
                        break
                    posicoes_digitadas[pos_int] = entry.player.nome
                except ValueError:
                    mensagem_erro = f"❌ Posição inválida para {entry.player.nome}. Use apenas números."
                    break
        
        # Se não houver erro, salvar
        if not mensagem_erro:
            for entry in entries:
                pid = entry.player.id
                pos_str = dados_post[pid]['pos']
                ajuste_str = dados_post[pid]['ajuste']
                prize_str = dados_post[pid]['prize']
                
                # Se tem posição, salva
                if pos_str:
                    try:
                        res, created = TournamentResult.objects.get_or_create(
                            tournament=tournament,
                            player=entry.player
                        )
                        
                        res.posicao = int(pos_str)
                        res.premiacao_recebida = Decimal(prize_str) if prize_str else Decimal("0")
                        res.pontos_ajuste_deal = int(ajuste_str) if ajuste_str else 0
                        res.save()
                    except Exception as e:
                        mensagem_erro = f"❌ Erro ao salvar resultado de {entry.player.nome}: {str(e)}"
                        break
                else:
                    # Se não tem posição, deleta resultado anterior
                    TournamentResult.objects.filter(tournament=tournament, player=entry.player).delete()
            
            if not mensagem_erro:
                mensagem = "✅ Resultados salvos com sucesso!"
                dados_post = {}  # Limpar dados_post após salvar com sucesso
    
    # Montar lista
    linhas = []
    entries = TournamentEntry.objects.filter(tournament=tournament).select_related("player").order_by("player__nome")
    for e in entries:
        r = TournamentResult.objects.filter(tournament=tournament, player=e.player).first()
        
        # Usar dados_post se existirem (quando há erro ou logo após POST)
        # Se não, usar dados do banco
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
                "ajuste_valor": r.pontos_ajuste_deal if r else "",
            }
        linhas.append(linha_dict)
        
    return render(request, "tournament_results.html", {
        "tournament": tournament,
        "season": season,
        "linhas": linhas,
        "mensagem": mensagem,
        "mensagem_erro": mensagem_erro,
    })