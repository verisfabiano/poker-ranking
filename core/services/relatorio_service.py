"""
Serviço para geração de relatórios de poker.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F, Max, Min
from django.utils import timezone
from core.models import (
    Report, ReportFinanceiro, ReportDesempenho, ReportRanking,
    Tournament, TournamentResult, TournamentEntry, Player,
    PlayerStatistics, TournamentPlayerPurchase, Season, Tenant
)
import json


class RelatorioService:
    """Serviço centralizado para geração de relatórios"""
    
    def __init__(self, tenant, usuario):
        self.tenant = tenant
        self.usuario = usuario
    
    # ================================================================
    # RELATÓRIO FINANCEIRO
    # ================================================================
    
    def gerar_relatorio_financeiro(self, data_inicio, data_fim, titulo=None):
        """Gera relatório financeiro para um período"""
        
        if not titulo:
            titulo = f"Relatório Financeiro {data_inicio} a {data_fim}"
        
        # Buscar torneios no período
        torneios = Tournament.objects.filter(
            season__tenant=self.tenant,
            data__date__gte=data_inicio,
            data__date__lte=data_fim,
            status='ENCERRADO'
        )
        
        # Calcular totais
        resultados = TournamentResult.objects.filter(tournament__in=torneios)
        entradas = TournamentEntry.objects.filter(tournament__in=torneios)
        rebuys_addons = TournamentPlayerPurchase.objects.filter(tournament__in=torneios)
        
        # Buy-in total
        total_buy_in = sum(
            t.buyin_valor * entradas.filter(tournament=t).count()
            for t in torneios
        )
        
        # Rebuys e Add-ons
        total_rebuy = rebuys_addons.filter(tipo='REBUY').aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        total_addon = rebuys_addons.filter(tipo='ADDON').aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        # Faturamento total
        total_faturamento = Decimal(str(total_buy_in)) + total_rebuy + total_addon
        
        # Premiações
        total_premiacao = resultados.aggregate(
            total=Sum('premiacao_recebida')
        )['total'] or Decimal('0')
        
        # Rake
        total_rake = total_faturamento - total_premiacao
        
        # Lucro
        lucro_liquido = total_rake
        
        # Detalhes por tipo de torneio
        detalhes_por_tipo = {}
        for torneio in torneios.distinct('tournament_type'):
            t_type = torneio.tournament_type
            t_torneios = torneios.filter(tournament_type=t_type)
            
            t_buy_in = sum(
                t.buyin_valor * entradas.filter(tournament=t).count()
                for t in t_torneios
            )
            t_rebuys = rebuys_addons.filter(
                tournament__in=t_torneios,
                tipo='REBUY'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            t_addons = rebuys_addons.filter(
                tournament__in=t_torneios,
                tipo='ADDON'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            
            t_faturamento = Decimal(str(t_buy_in)) + t_rebuys + t_addons
            t_premiacao = resultados.filter(
                tournament__in=t_torneios
            ).aggregate(total=Sum('premiacao_recebida'))['total'] or Decimal('0')
            
            detalhes_por_tipo[str(t_type)] = {
                'buy_in': float(t_buy_in),
                'rebuy': float(t_rebuys),
                'addon': float(t_addons),
                'faturamento': float(t_faturamento),
                'premiacao': float(t_premiacao),
                'rake': float(t_faturamento - t_premiacao),
            }
        
        # Margem bruta
        margem = (float(total_rake) / float(total_faturamento) * 100) if total_faturamento > 0 else 0
        
        # Criar relatório
        report = Report.objects.create(
            tenant=self.tenant,
            tipo='FINANCEIRO',
            periodo='CUSTOMIZADO',
            data_inicio=data_inicio,
            data_fim=data_fim,
            titulo=titulo,
            gerado_por=self.usuario,
            dados={
                'total_buy_in': float(total_buy_in),
                'total_rebuy': float(total_rebuy),
                'total_addon': float(total_addon),
                'total_faturamento': float(total_faturamento),
                'total_premiacao': float(total_premiacao),
                'total_rake': float(total_rake),
                'lucro_liquido': float(lucro_liquido),
            }
        )
        
        # Criar relatório financeiro específico
        ReportFinanceiro.objects.create(
            report=report,
            total_buy_in=total_buy_in,
            total_rebuy=total_rebuy,
            total_addon=total_addon,
            total_faturamento=total_faturamento,
            total_premiacao=total_premiacao,
            total_rake=total_rake,
            lucro_liquido=lucro_liquido,
            numero_torneios=torneios.count(),
            numero_jogadores_unicos=entradas.values('player').distinct().count(),
            ticket_medio=total_faturamento / torneios.count() if torneios.count() > 0 else Decimal('0'),
            detalhes_por_tipo=detalhes_por_tipo,
            margem_bruta=Decimal(str(margem)),
        )
        
        return report
    
    # ================================================================
    # RELATÓRIO DE DESEMPENHO
    # ================================================================
    
    def gerar_relatorio_desempenho(self, player, season, data_inicio, data_fim):
        """Gera relatório de desempenho de um jogador"""
        
        # Buscar resultados do jogador no período
        resultados = TournamentResult.objects.filter(
            player=player,
            tournament__season=season,
            tournament__data__date__gte=data_inicio,
            tournament__data__date__lte=data_fim,
        ).select_related('tournament')
        
        # Estatísticas
        total_participacoes = resultados.count()
        total_vitórias = resultados.filter(posicao=1).count()
        total_top3 = resultados.filter(posicao__lte=3).count()
        
        # Financeiro
        total_investido = Decimal('0')
        total_ganho = resultados.aggregate(
            total=Sum('premiacao_recebida')
        )['total'] or Decimal('0')
        
        # Calcular investimento (buy-in + rebuys + addons)
        for resultado in resultados:
            t = resultado.tournament
            total_investido += t.buyin_valor or Decimal('0')
            
            # Add rebuys
            rebuys = TournamentPlayerPurchase.objects.filter(
                tournament=t,
                player=player,
                tipo='REBUY'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            
            addons = TournamentPlayerPurchase.objects.filter(
                tournament=t,
                player=player,
                tipo='ADDON'
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            
            total_investido += rebuys + addons
        
        # ROI
        roi = Decimal('0')
        if total_investido > 0:
            roi = ((total_ganho - total_investido) / total_investido) * 100
        
        # Análise de posições
        posicoes = list(resultados.values_list('posicao', flat=True).order_by('posicao'))
        melhor_posicao = min(posicoes) if posicoes else None
        pior_posicao = max(posicoes) if posicoes else None
        posicao_media = sum(posicoes) / len(posicoes) if posicoes else None
        
        # Evolução de pontos (por dia)
        stats = PlayerStatistics.objects.filter(
            player=player,
            season=season
        ).first()
        
        evolucao_pontos = []
        lucro_por_dia = {}
        
        for resultado in resultados.order_by('tournament__data'):
            data_str = resultado.tournament.data.strftime('%Y-%m-%d')
            
            evolucao_pontos.append({
                'data': data_str,
                'torneio': resultado.tournament.nome,
                'posicao': resultado.posicao,
                'pontos': resultado.pontos_finais,
            })
            
            if data_str not in lucro_por_dia:
                lucro_por_dia[data_str] = Decimal('0')
            
            lucro_por_dia[data_str] += (resultado.premiacao_recebida or Decimal('0'))
        
        # Criar relatório
        titulo = f"Desempenho de {player.nome} ({season.nome})"
        report = Report.objects.create(
            tenant=self.tenant,
            tipo='DESEMPENHO_JOGADOR',
            periodo='CUSTOMIZADO',
            data_inicio=data_inicio,
            data_fim=data_fim,
            titulo=titulo,
            gerado_por=self.usuario,
            filtros={'player_id': player.id, 'season_id': season.id},
            dados={
                'participacoes': total_participacoes,
                'vitórias': total_vitórias,
                'top_3': total_top3,
                'investido': float(total_investido),
                'ganho': float(total_ganho),
                'roi': float(roi),
            }
        )
        
        # Criar relatório de desempenho
        total_pontos_stats = stats.pontos_totais if stats else 0
        
        ReportDesempenho.objects.create(
            report=report,
            player=player,
            season=season,
            total_participacoes=total_participacoes,
            total_vitórias=total_vitórias,
            total_top3=total_top3,
            total_pontos=total_pontos_stats,
            total_investido=total_investido,
            total_ganho=total_ganho,
            roi=roi,
            melhor_posicao=melhor_posicao,
            pior_posicao=pior_posicao,
            posicao_media=Decimal(str(posicao_media)) if posicao_media else None,
            evolucao_pontos=evolucao_pontos,
            lucro_por_dia={k: float(v) for k, v in lucro_por_dia.items()},
        )
        
        return report
    
    # ================================================================
    # RELATÓRIO DE RANKING
    # ================================================================
    
    def gerar_relatorio_ranking(self, season, data_inicio, data_fim):
        """Gera relatório do ranking em um período"""
        
        # Top 10
        stats = PlayerStatistics.objects.filter(
            season=season,
            tenant=self.tenant
        ).order_by('-pontos_totais')[:10]
        
        top_10 = []
        for idx, stat in enumerate(stats, 1):
            top_10.append({
                'posicao': idx,
                'nome': stat.player.nome,
                'apelido': stat.player.apelido,
                'pontos': stat.pontos_totais,
                'vitórias': stat.vitórias,
                'participacoes': stat.participacoes,
                'roi': float(stat.roi) if stat.roi else 0,
            })
        
        # Total de jogadores
        total_jogadores = PlayerStatistics.objects.filter(
            season=season,
            tenant=self.tenant
        ).count()
        
        # Total de pontos
        total_pontos = PlayerStatistics.objects.filter(
            season=season,
            tenant=self.tenant
        ).aggregate(total=Sum('pontos_totais'))['total'] or 0
        
        # Média de pontos
        pontos_medio = total_pontos / total_jogadores if total_jogadores > 0 else 0
        
        # Maiores subidas e quedas (comparar com semana anterior)
        data_inicio_anterior = data_inicio - timedelta(days=7)
        
        # Simplificado: maiores vencedores na semana
        maiores_subidas = TournamentResult.objects.filter(
            player__playerturn__season=season,
            tournament__data__date__gte=data_inicio,
            tournament__data__date__lte=data_fim,
            posicao=1
        ).values('player__nome').annotate(
            vitórias=Count('id')
        ).order_by('-vitórias')[:5]
        
        maiores_quedas = []  # Simplificado
        
        # Criar relatório
        titulo = f"Ranking {season.nome} ({data_inicio} a {data_fim})"
        report = Report.objects.create(
            tenant=self.tenant,
            tipo='RANKING',
            periodo='CUSTOMIZADO',
            data_inicio=data_inicio,
            data_fim=data_fim,
            titulo=titulo,
            gerado_por=self.usuario,
            filtros={'season_id': season.id},
            dados={
                'total_jogadores': total_jogadores,
                'total_pontos': total_pontos,
                'pontos_medio': float(pontos_medio),
            }
        )
        
        # Criar relatório de ranking
        ReportRanking.objects.create(
            report=report,
            season=season,
            top_10=top_10,
            total_jogadores=total_jogadores,
            total_pontos_distribuidos=total_pontos,
            pontos_medio_por_jogador=Decimal(str(pontos_medio)),
            maiores_subidas=list(maiores_subidas),
            maiores_quedas=maiores_quedas,
        )
        
        return report
    
    # ================================================================
    # UTILITÁRIOS
    # ================================================================
    
    def listar_relatorios(self, tipo=None, limite=20):
        """Lista relatórios disponíveis"""
        query = Report.objects.filter(tenant=self.tenant)
        
        if tipo:
            query = query.filter(tipo=tipo)
        
        return query[:limite]
    
    def deletar_relatorio(self, report_id):
        """Deleta um relatório"""
        report = Report.objects.get(id=report_id, tenant=self.tenant)
        report.delete()
