"""
Views para relatórios de poker.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import json

from .ranking import tenant_required
from core.models import (
    Report, ReportFinanceiro, ReportDesempenho, ReportRanking,
    Season, Player, Tournament
)
from core.services.relatorio_service import RelatorioService


@login_required
@tenant_required
def relatorios_home(request):
    """Dashboard de relatórios"""
    
    # Últimos 10 relatórios
    relatorios = Report.objects.filter(
        tenant=request.tenant
    )[:10]
    
    # Contar por tipo
    stats_tipos = {}
    for tipo, nome in Report._meta.get_field('tipo').choices:
        count = Report.objects.filter(tenant=request.tenant, tipo=tipo).count()
        stats_tipos[nome] = count
    
    context = {
        'relatorios': relatorios,
        'stats_tipos': stats_tipos,
        'total_relatorios': Report.objects.filter(tenant=request.tenant).count(),
    }
    
    return render(request, 'relatorios/home.html', context)


@login_required
@tenant_required
def relatorios_listar(request):
    """Lista todos os relatórios com filtros"""
    
    relatorios = Report.objects.filter(tenant=request.tenant)
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        relatorios = relatorios.filter(tipo=tipo)
    
    periodo = request.GET.get('periodo')
    if periodo:
        relatorios = relatorios.filter(periodo=periodo)
    
    # Ordenação
    order = request.GET.get('order', '-criado_em')
    relatorios = relatorios.order_by(order)
    
    context = {
        'relatorios': relatorios,
        'tipo_selecionado': tipo,
        'periodo_selecionado': periodo,
        'tipos': dict(Report._meta.get_field('tipo').choices),
        'periodos': dict(Report._meta.get_field('periodo').choices),
    }
    
    return render(request, 'relatorios/listar.html', context)


@login_required
@tenant_required
def relatorio_detalhe(request, report_id):
    """Visualiza um relatório específico"""
    
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    # Buscar dados específicos por tipo
    dados_especificos = None
    
    if report.tipo == 'FINANCEIRO':
        dados_especificos = ReportFinanceiro.objects.get(report=report)
    elif report.tipo == 'DESEMPENHO_JOGADOR':
        dados_especificos = ReportDesempenho.objects.get(report=report)
    elif report.tipo == 'RANKING':
        dados_especificos = ReportRanking.objects.get(report=report)
    
    context = {
        'report': report,
        'dados_especificos': dados_especificos,
        'tipo_nome': dict(Report._meta.get_field('tipo').choices).get(report.tipo),
    }
    
    return render(request, 'relatorios/detalhe.html', context)


@login_required
@tenant_required
@require_http_methods(["GET", "POST"])
def gerar_relatorio_financeiro(request):
    """Gera um novo relatório financeiro"""
    
    # Verificar permissão
    tenant_user = request.user.tenant_users.filter(tenant=request.tenant).first()
    if tenant_user and tenant_user.role != 'admin':
        return render(request, 'erro.html', {'mensagem': 'Permissão negada'}, status=403)
    
    if request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        titulo = request.POST.get('titulo', '')
        
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            
            if data_inicio > data_fim:
                return render(request, 'relatorios/gerar_financeiro.html', {
                    'erro': 'Data de início não pode ser posterior à data de fim'
                })
            
            # Gerar relatório
            service = RelatorioService(request.tenant, request.user)
            report = service.gerar_relatorio_financeiro(data_inicio, data_fim, titulo)
            
            return redirect('relatorio_detalhe', report_id=report.id)
        
        except Exception as e:
            return render(request, 'relatorios/gerar_financeiro.html', {
                'erro': str(e)
            })
    
    # GET - mostrar formulário
    data_fim_padrao = datetime.now().date()
    data_inicio_padrao = data_fim_padrao - timedelta(days=30)
    
    context = {
        'data_inicio_padrao': data_inicio_padrao,
        'data_fim_padrao': data_fim_padrao,
    }
    
    return render(request, 'relatorios/gerar_financeiro.html', context)


@login_required
@tenant_required
@require_http_methods(["GET", "POST"])
def gerar_relatorio_desempenho(request):
    """Gera um novo relatório de desempenho"""
    
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        season_id = request.POST.get('season_id')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        
        try:
            player = get_object_or_404(Player, id=player_id, tenant=request.tenant)
            season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            
            # Gerar relatório
            service = RelatorioService(request.tenant, request.user)
            report = service.gerar_relatorio_desempenho(player, season, data_inicio, data_fim)
            
            return redirect('relatorio_detalhe', report_id=report.id)
        
        except Exception as e:
            jogadores = Player.objects.filter(tenant=request.tenant).order_by('nome')
            temporadas = Season.objects.filter(tenant=request.tenant).order_by('-data_inicio')
            return render(request, 'relatorios/gerar_desempenho.html', {
                'erro': str(e),
                'players': jogadores,
                'seasons': temporadas,
            })
    
    # GET - mostrar formulário
    jogadores = Player.objects.filter(tenant=request.tenant).order_by('nome')
    temporadas = Season.objects.filter(tenant=request.tenant).order_by('-data_inicio')
    
    data_fim_padrao = datetime.now().date()
    data_inicio_padrao = data_fim_padrao - timedelta(days=30)
    
    context = {
        'players': jogadores,
        'seasons': temporadas,
        'data_inicio': data_inicio_padrao,
        'data_fim': data_fim_padrao,
    }
    
    return render(request, 'relatorios/gerar_desempenho.html', context)


@login_required
@tenant_required
@require_http_methods(["GET", "POST"])
def gerar_relatorio_ranking(request):
    """Gera um novo relatório de ranking"""
    
    if request.method == 'POST':
        season_id = request.POST.get('season_id')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        
        try:
            season = get_object_or_404(Season, id=season_id, tenant=request.tenant)
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            
            # Gerar relatório
            service = RelatorioService(request.tenant, request.user)
            report = service.gerar_relatorio_ranking(season, data_inicio, data_fim)
            
            return redirect('relatorio_detalhe', report_id=report.id)
        
        except Exception as e:
            temporadas = Season.objects.filter(tenant=request.tenant).order_by('-data_inicio')
            return render(request, 'relatorios/gerar_ranking.html', {
                'erro': str(e),
                'seasons': temporadas,
            })
    
    # GET
    temporadas = Season.objects.filter(tenant=request.tenant).order_by('-data_inicio')
    
    data_fim_padrao = datetime.now().date()
    data_inicio_padrao = data_fim_padrao - timedelta(days=7)
    
    context = {
        'seasons': temporadas,
        'data_inicio': data_inicio_padrao,
        'data_fim': data_fim_padrao,
    }
    
    return render(request, 'relatorios/gerar_ranking.html', context)


@login_required
@tenant_required
def exportar_relatorio_csv(request, report_id):
    """Exporta relatório como CSV"""
    
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{report.id}.csv"'
    
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow(['Relatório:', report.titulo])
    writer.writerow(['Período:', f"{report.data_inicio} a {report.data_fim}"])
    writer.writerow(['Gerado em:', report.criado_em.strftime('%d/%m/%Y %H:%M')])
    writer.writerow([])
    
    # Dados específicos
    if report.tipo == 'FINANCEIRO':
        fin = ReportFinanceiro.objects.get(report=report)
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Total Buy-in', f"R$ {fin.total_buy_in:.2f}"])
        writer.writerow(['Total Rebuy', f"R$ {fin.total_rebuy:.2f}"])
        writer.writerow(['Total Add-on', f"R$ {fin.total_addon:.2f}"])
        writer.writerow(['Total Faturamento', f"R$ {fin.total_faturamento:.2f}"])
        writer.writerow(['Total Premiação', f"R$ {fin.total_premiacao:.2f}"])
        writer.writerow(['Rake Total', f"R$ {fin.total_rake:.2f}"])
        writer.writerow(['Lucro Líquido', f"R$ {fin.lucro_liquido:.2f}"])
        writer.writerow(['Margem Bruta', f"{fin.margem_bruta:.2f}%"])
        writer.writerow(['Número de Torneios', fin.numero_torneios])
        writer.writerow(['Jogadores Únicos', fin.numero_jogadores_unicos])
    
    elif report.tipo == 'DESEMPENHO_JOGADOR':
        des = ReportDesempenho.objects.get(report=report)
        writer.writerow(['Jogador:', des.player.nome])
        writer.writerow(['Temporada:', des.season.nome])
        writer.writerow([])
        writer.writerow(['Métrica', 'Valor'])
        writer.writerow(['Participações', des.total_participacoes])
        writer.writerow(['Vitórias', des.total_vitórias])
        writer.writerow(['Top 3', des.total_top3])
        writer.writerow(['Total Investido', f"R$ {des.total_investido:.2f}"])
        writer.writerow(['Total Ganho', f"R$ {des.total_ganho:.2f}"])
        writer.writerow(['ROI', f"{des.roi:.2f}%"])
    
    elif report.tipo == 'RANKING':
        rank = ReportRanking.objects.get(report=report)
        writer.writerow(['Ranking:', rank.season.nome])
        writer.writerow([])
        writer.writerow(['Posição', 'Jogador', 'Pontos', 'Vitórias', 'Participações'])
        for item in rank.top_10:
            writer.writerow([
                item['posicao'],
                item['nome'],
                item['pontos'],
                item['vitórias'],
                item['participacoes']
            ])
    
    return response


@login_required
@tenant_required
def relatorio_json(request, report_id):
    """Retorna dados do relatório em JSON (para gráficos)"""
    
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    data = {
        'id': report.id,
        'titulo': report.titulo,
        'tipo': report.tipo,
        'data_inicio': report.data_inicio.isoformat(),
        'data_fim': report.data_fim.isoformat(),
        'dados': report.dados,
    }
    
    # Adicionar dados específicos
    if report.tipo == 'FINANCEIRO':
        fin = ReportFinanceiro.objects.get(report=report)
        data['especifico'] = {
            'total_buy_in': float(fin.total_buy_in),
            'total_rebuy': float(fin.total_rebuy),
            'total_addon': float(fin.total_addon),
            'total_faturamento': float(fin.total_faturamento),
            'total_premiacao': float(fin.total_premiacao),
            'total_rake': float(fin.total_rake),
            'margem_bruta': float(fin.margem_bruta),
            'detalhes_por_tipo': fin.detalhes_por_tipo,
        }
    
    elif report.tipo == 'DESEMPENHO_JOGADOR':
        des = ReportDesempenho.objects.get(report=report)
        data['especifico'] = {
            'player_nome': des.player.nome,
            'participacoes': des.total_participacoes,
            'vitórias': des.total_vitórias,
            'top_3': des.total_top3,
            'investido': float(des.total_investido),
            'ganho': float(des.total_ganho),
            'roi': float(des.roi),
            'evolucao_pontos': des.evolucao_pontos,
            'lucro_por_dia': des.lucro_por_dia,
        }
    
    elif report.tipo == 'RANKING':
        rank = ReportRanking.objects.get(report=report)
        data['especifico'] = {
            'season_nome': rank.season.nome,
            'total_jogadores': rank.total_jogadores,
            'top_10': rank.top_10,
            'maiores_subidas': rank.maiores_subidas,
        }
    
    return JsonResponse(data)


@login_required
@tenant_required
def deletar_relatorio(request, report_id):
    """Deleta um relatório"""
    
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    # Verificar permissão
    tenant_user = request.user.tenant_users.filter(tenant=request.tenant).first()
    if tenant_user and tenant_user.role != 'admin':
        return render(request, 'erro.html', {'mensagem': 'Permissão negada'}, status=403)
    
    if request.method == 'POST':
        report.delete()
        return redirect('relatorios_listar')
    
    return render(request, 'relatorios/confirmar_deletar.html', {'report': report})
