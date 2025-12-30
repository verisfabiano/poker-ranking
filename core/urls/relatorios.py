"""
URLs para o módulo de relatórios.
"""

from django.urls import path
from core.views import relatorios

urlpatterns = [
    # Dashboard de relatórios
    path('', relatorios.relatorios_home, name='relatorios_home'),
    path('listar/', relatorios.relatorios_listar, name='relatorios_listar'),
    
    # Visualizar relatório
    path('<int:report_id>/', relatorios.relatorio_detalhe, name='relatorio_detalhe'),
    path('<int:report_id>/json/', relatorios.relatorio_json, name='relatorio_json'),
    path('<int:report_id>/exportar-csv/', relatorios.exportar_relatorio_csv, name='exportar_relatorio_csv'),
    path('<int:report_id>/deletar/', relatorios.deletar_relatorio, name='deletar_relatorio'),
    
    # Gerar relatórios
    path('gerar/financeiro/', relatorios.gerar_relatorio_financeiro, name='gerar_relatorio_financeiro'),
    path('gerar/desempenho/', relatorios.gerar_relatorio_desempenho, name='gerar_relatorio_desempenho'),
    path('gerar/ranking/', relatorios.gerar_relatorio_ranking, name='gerar_relatorio_ranking'),
]
