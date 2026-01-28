from django.urls import path, include
from django.views.generic import RedirectView
from django.shortcuts import render

from .views.public import landing_page, signup_club, login_view
from .views.superadmin import (
    superadmin_dashboard,
    superadmin_tenants_list,
    superadmin_tenant_create,
    superadmin_tenant_detail,
    superadmin_tenant_edit,
    superadmin_tenant_delete,
    superadmin_tenant_admin_add,
    superadmin_tenant_admin_remove,
)
from .views.player_public import player_register_public, player_login_club
from .views.documentacao import documentacao_ranking
from .views.financial_enhanced import (
    reconciliar_torneio,
    saldo_caixa_diario,
    relatorio_financeiro_completo,
    api_financial_reconciliation,
)
from .views.prize import (
    prize_distribution_view,
    update_prize_config,
    apply_prize_template,
    set_prize_payment,
    assign_player_to_prize,
    finalize_prize_distribution,
    view_prize_summary,
)
from .views.auth import (
    verify_email,
    forgot_password,
    reset_password,
    resend_verification_email,
)
from .views import (
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
    tournament_admin_panel,
    tournament_result_modal,
    tournament_result_save,
    tournament_create_wizard_step_data,
    tournament_create_wizard_save,
    tournament_duplicate,
    tournament_batch_import,
    tournament_save_template,
    tournament_draft_save,
    tournament_undo_action,
    tournament_create_series,
    tournament_edit_from_template,
    
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
    tournament_rebuy_history,

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
    #  SUPERADMIN - GERENCIAMENTO DE TENANTS
    # ============================================================
    path("superadmin/", superadmin_dashboard, name="superadmin_dashboard"),
    path("superadmin/tenants/", superadmin_tenants_list, name="superadmin_tenants_list"),
    path("superadmin/tenants/novo/", superadmin_tenant_create, name="superadmin_tenant_create"),
    path("superadmin/tenants/<int:tenant_id>/", superadmin_tenant_detail, name="superadmin_tenant_detail"),
    path("superadmin/tenants/<int:tenant_id>/editar/", superadmin_tenant_edit, name="superadmin_tenant_edit"),
    path("superadmin/tenants/<int:tenant_id>/deletar/", superadmin_tenant_delete, name="superadmin_tenant_delete"),
    path("superadmin/tenants/<int:tenant_id>/admin/adicionar/", superadmin_tenant_admin_add, name="superadmin_tenant_admin_add"),
    path("superadmin/tenants/<int:tenant_id>/admin/<int:user_id>/remover/", superadmin_tenant_admin_remove, name="superadmin_tenant_admin_remove"),

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
    path("api/season/<int:season_id>/tournament/wizard/step/<int:step>/", tournament_create_wizard_step_data, name="tournament_wizard_step"),
    path("api/season/<int:season_id>/tournament/wizard/save/", tournament_create_wizard_save, name="tournament_wizard_save"),
    path("torneio/<int:tournament_id>/editar/", tournament_edit, name="tournament_edit"),
    path("torneio/<int:tournament_id>/admin/", tournament_admin_panel, name="tournament_admin_panel"),
    path("api/torneio/<int:tournament_id>/jogador/<int:player_id>/modal-resultado/", tournament_result_modal, name="tournament_result_modal"),
    path("api/torneio/<int:tournament_id>/resultado/salvar/", tournament_result_save, name="tournament_result_save"),
    path("torneio/<int:tournament_id>/jogadores/", tournament_entries_manage, name="tournament_entries_manage"),
    path("torneio/<int:tournament_id>/lancamento/", tournament_results, name="tournament_results"),
    
    # ============================================================
    #  PHASE 5: BATCH TOURNAMENT CREATION
    # ============================================================
    path("torneio/<int:tournament_id>/duplicar/", tournament_duplicate, name="tournament_duplicate"),
    path("season/<int:season_id>/torneios/importar-csv/", tournament_batch_import, name="tournament_batch_import"),
    path("torneio/<int:tournament_id>/salvar-template/", tournament_save_template, name="tournament_save_template"),
    
    # ============================================================
    #  PHASE 6: ADVANCED FEATURES
    # ============================================================
    path("api/season/<int:season_id>/torneios/rascunho/", tournament_draft_save, name="tournament_draft_save"),
    path("api/torneio/<int:tournament_id>/desfazer/", tournament_undo_action, name="tournament_undo"),
    path("season/<int:season_id>/torneios/serie/", tournament_create_series, name="tournament_create_series"),
    path("torneio/<int:tournament_id>/editar-modelo/", tournament_edit_from_template, name="tournament_edit_template"),
    
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
    path("api/torneio/<int:tournament_id>/jogador/<int:player_id>/rebuy-history/", tournament_rebuy_history, name="tournament_rebuy_history"),

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
    path("auth/verify-email/<str:token>/", verify_email, name="verify_email"),
    path("auth/resend-verification-email/", resend_verification_email, name="resend_verification_email"),
    path("auth/forgot-password/", forgot_password, name="forgot_password"),
    path("auth/reset-password/<str:token>/", reset_password, name="reset_password"),
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