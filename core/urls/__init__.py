from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import render

from core.views.public import landing_page, signup_club, login_view
from core.views.superadmin import clientes_list, cliente_detail, cliente_slug_update, cliente_toggle_status
from core.views.player_public import player_register_public, player_login_club
from core.views.documentacao import documentacao_ranking
from core.views.financial_enhanced import (
    reconciliar_torneio,
    saldo_caixa_diario,
    relatorio_financeiro_completo,
    api_financial_reconciliation,
)
from core.views.prize import (
    prize_distribution_view,
    update_prize_config,
    apply_prize_template,
    set_prize_payment,
    assign_player_to_prize,
    finalize_prize_distribution,
    view_prize_summary,
)
from core.views import (
    home_redirect,
    ranking_season,
    tv_ranking_season,
    painel_home,
    tv_dashboard,

    # Temporadas
    seasons_list,
    season_create,
    season_edit,
    season_initial_points,
    player_progress_season,
    api_seasons,

    # Tipos de torneio
    tournament_types_list,
    tournament_type_create,
    tournament_type_edit,

    # Torneios
    tournaments_list_all,
    season_tournaments,
    tournament_dashboard,
    tournament_create,
    tournament_edit,
    tournament_entries_manage,
    tournament_results,
    
    # Produtos de Torneio
    tournament_products_list,
    tournament_product_create,
    tournament_product_edit,
    tournament_product_delete,
    tournament_product_sales,
    tournament_product_purchase_add,
    tournament_product_purchase_delete,
    tournament_add_rebuy_addon,
    tournament_remove_rebuy_addon,

    # Jogadores
    player_home,
    player_login,
    player_logout,
    players_list,
    player_create,
    player_create_quick,
    player_edit,
    player_profile,
    player_register,
    player_tournaments,
    confirm_presence,
    select_tenant_register,
    club_edit,

    # Blinds
    blind_structures_list,
    blind_structure_create,
    blind_structure_manage,
    clone_blind_structure,
    
    # Diretor de torneio
    director_panel,
    director_toggle_timer,
    director_change_level,
    api_tournament_status,
    tournament_update_status,

    # Financeiro
    tournament_financial,
    financial_dashboard,
    season_financial,
    financial_by_period,
    api_financial_summary,

    # Ranking avançado
    ranking_avancado,
    api_ranking_json,
    estatisticas_jogador,
)

urlpatterns = [
    # Raiz do site -> Landing page
    path("", landing_page, name="landing_page"),
    path("signup/", signup_club, name="signup_club"),
    path("login/", login_view, name="login"),

    # Raiz do site -> decide pra onde mandar (admin x jogador)
    path("redirect/", home_redirect, name="home_redirect"),

    # ============================================================
    #  SUPERADMIN - GERENCIAMENTO DE CLIENTES
    # ============================================================
    path("superadmin/clientes/", clientes_list, name="clientes_list"),
    path("superadmin/clientes/<int:cliente_id>/", cliente_detail, name="cliente_detail"),
    path("superadmin/clientes/<int:cliente_id>/slug/", cliente_slug_update, name="cliente_slug_update"),
    path("superadmin/clientes/<int:cliente_id>/status/", cliente_toggle_status, name="cliente_toggle_status"),

    # ============================================================
    #  ADMIN - PAINEL
    # ============================================================
    path("painel/", painel_home, name="painel_home"),

    # ============================================================
    #  RANKING (PÚBLICO)
    # ============================================================
    path("ranking/<int:season_id>/", ranking_season, name="ranking_season"),
    path("tv/ranking/<int:season_id>/", tv_ranking_season, name="tv_ranking_season"),

    # ============================================================
    #  TEMPORADAS (ADMIN)
    # ============================================================
    path("temporadas/", seasons_list, name="seasons_list"),
    path("temporadas/nova/", season_create, name="season_create"),
    path("temporadas/editar/<int:season_id>/", season_edit, name="season_edit"),
    path("temporadas/<int:season_id>/pontos-iniciais/", season_initial_points, name="season_initial_points"),
    path("api/seasons/", api_seasons, name="api_seasons"),

    # ============================================================
    #  TIPOS DE TORNEIO (ADMIN)
    # ============================================================
    path("tipos-torneio/", tournament_types_list, name="tournament_types_list"),
    path("tipos-torneio/novo/", tournament_type_create, name="tournament_type_create"),
    path("tipos-torneio/editar/<int:tipo_id>/", tournament_type_edit, name="tournament_type_edit"),

    # ============================================================
    #  TORNEIOS (ADMIN)
    # ============================================================
    path("torneios/", tournaments_list_all, name="tournaments_list_all"),
    path("torneios/dashboard/", tournament_dashboard, name="tournament_dashboard"),
    path("season/<int:season_id>/torneios/", season_tournaments, name="season_tournaments"),
    path("season/<int:season_id>/torneios/novo/", tournament_create, name="tournament_create"),
    path("torneio/<int:tournament_id>/editar/", tournament_edit, name="tournament_edit"),
    path("torneio/<int:tournament_id>/jogadores/", tournament_entries_manage, name="tournament_entries_manage"),
    path("torneio/<int:tournament_id>/lancamento/", tournament_results, name="tournament_results"),
    
    # ============================================================
    #  PRODUTOS DE TORNEIO
    # ============================================================
    path("produtos/", tournament_products_list, name="tournament_products_list"),
    path("produtos/novo/", tournament_product_create, name="tournament_product_create"),
    path("produtos/<int:product_id>/editar/", tournament_product_edit, name="tournament_product_edit"),
    path("produtos/<int:product_id>/deletar/", tournament_product_delete, name="tournament_product_delete"),
    path("torneio/<int:tournament_id>/vendas-produtos/", tournament_product_sales, name="tournament_product_sales"),
    path("venda-produto/adicionar/", tournament_product_purchase_add, name="tournament_product_purchase_add"),
    path("venda-produto/<int:purchase_id>/deletar/", tournament_product_purchase_delete, name="tournament_product_purchase_delete"),
    path("api/torneio/<int:tournament_id>/rebuy-addon/", tournament_add_rebuy_addon, name="tournament_add_rebuy_addon"),
    path("api/torneio/<int:tournament_id>/rebuy-addon/remove/", tournament_remove_rebuy_addon, name="tournament_remove_rebuy_addon"),

    # ============================================================
    #  PREMIAÇÃO (ADMIN)
    # ============================================================
    path("torneio/<int:tournament_id>/premiacao/", prize_distribution_view, name="prize_distribution"),
    path("api/torneio/<int:tournament_id>/premiacao/config/", update_prize_config, name="update_prize_config"),
    path("api/torneio/<int:tournament_id>/premiacao/template/", apply_prize_template, name="apply_prize_template"),
    path("api/torneio/<int:tournament_id>/premiacao/posicao/", set_prize_payment, name="set_prize_payment"),
    path("api/torneio/<int:tournament_id>/premiacao/jogador/", assign_player_to_prize, name="assign_player_to_prize"),
    path("api/torneio/<int:tournament_id>/premiacao/finalizar/", finalize_prize_distribution, name="finalize_prize_distribution"),
    path("torneio/<int:tournament_id>/premiacao/resumo/", view_prize_summary, name="prize_summary"),

    # ============================================================
    #  JOGADORES (PORTAL DO JOGADOR)
    # ============================================================
    path("jogador/home/", player_home, name="player_home"),
    path("jogador/login/", player_login, name="player_login"),
    path("jogador/logout/", player_logout, name="player_logout"),
    path("jogador/selecionar-clube/", select_tenant_register, name="select_tenant_register"),
    path("jogador/cadastro/", player_register, name="player_register"),
    path("jogador/torneios/", player_tournaments, name="player_tournaments"),
    path("jogador/confirmar/<int:tournament_id>/", confirm_presence, name="confirm_presence"),
    path("jogador/<int:player_id>/season/<int:season_id>/evolucao/", player_progress_season, name="player_progress_season"),

    # REGISTRO PÚBLICO DE JOGADORES POR CLUBE
    path("clube/<str:slug>/registro/", player_register_public, name="player_register_public"),
    path("clube/<str:slug>/login/", player_login_club, name="player_login_club"),

    # ============================================================
    #  JOGADORES (ADMIN)
    # ============================================================
    path("jogadores/", players_list, name="players_list"),
    path("jogadores/novo/", player_create, name="player_create"),
    path("jogadores/novo/rapido/", player_create_quick, name="player_create_quick"),
    path("jogadores/editar/<int:player_id>/", player_edit, name="player_edit"),
    path("meu-perfil/", player_profile, name="player_profile"),

    # ============================================================
    #  CLUB/TENANT (ADMIN)
    # ============================================================
    path("clube/", club_edit, name="club_edit"),

    # ============================================================
    #  BLINDS (ADMIN)
    # ============================================================
    path("blinds/", blind_structures_list, name="blind_structures_list"),
    path("blinds/nova/", blind_structure_create, name="blind_structure_create"),
    path("blinds/clonar/<int:template_id>/", clone_blind_structure, name="clone_blind_structure"),
    path("blinds/<int:structure_id>/gerenciar/", blind_structure_manage, name="blind_structure_manage"),

    # ============================================================
    #  DIRETOR DE TORNEIO
    # ============================================================
    path("torneio/<int:tournament_id>/diretor/", director_panel, name="director_panel"),
    path("torneio/<int:tournament_id>/timer/toggle/", director_toggle_timer, name="director_toggle_timer"),
    path("torneio/<int:tournament_id>/nivel/<str:direction>/", director_change_level, name="director_change_level"),
    path("api/torneio/<int:tournament_id>/status/", api_tournament_status, name="api_tournament_status"),
    path("api/torneio/<int:tournament_id>/status/update/", tournament_update_status, name="tournament_update_status"),
    path("torneio/<int:tournament_id>/telao/", tv_dashboard, name="tv_dashboard"),

    # ============================================================
    #  FINANCEIRO (ADMIN)
    # ============================================================
    path("torneio/<int:tournament_id>/financeiro/", tournament_financial, name="tournament_financial"),
    path("torneio/<int:tournament_id>/financeiro/reconciliar/", reconciliar_torneio, name="reconciliar_torneio"),
    path("financeiro/", financial_dashboard, name="financial_dashboard"),
    path("financeiro/temporada/<int:season_id>/", season_financial, name="season_financial"),
    path("financeiro/periodo/", financial_by_period, name="financial_by_period"),
    path("financeiro/caixa-diario/", saldo_caixa_diario, name="saldo_caixa_diario"),
    path("financeiro/relatorio-completo/", relatorio_financeiro_completo, name="relatorio_financeiro_completo"),
    path("api/financeiro/resumo/", api_financial_summary, name="api_financial_summary"),
    path("api/financeiro/reconciliacao/", api_financial_reconciliation, name="api_financial_reconciliation"),

    # ============================================================
    #  DOCUMENTAÇÃO
    # ============================================================
    path("ranking/documentacao/", documentacao_ranking, name="documentacao_ranking"),

    # ============================================================
    #  ATALHO /login/ (compatibilidade)
    # ============================================================
    path("login/", RedirectView.as_view(pattern_name="player_login", permanent=False), name="login_redirect"),

    # ============================================================
    #  RANKING AVANÇADO (JOGADOR)
    # ============================================================
    path("ranking/<int:season_id>/avancado/", ranking_avancado, name="ranking_avancado"),
    path("ranking/<int:season_id>/jogador/<int:player_id>/", estatisticas_jogador, name="estatisticas_jogador"),
    path("api/ranking/<int:season_id>/json/", api_ranking_json, name="api_ranking_json"),

    # ============================================================
    #  RELATÓRIOS (ADMIN)
    # ============================================================
    path("relatorios/", include("core.urls.relatorios")),
]