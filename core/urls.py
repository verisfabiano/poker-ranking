from django.urls import path
from django.views.generic import RedirectView

from .views import (
    home_redirect,
    ranking_season,
    tv_ranking_season,
    painel_home,

    # Temporadas
    seasons_list,
    season_create,
    season_edit,
    season_initial_points,
    player_progress_season,

    # Tipos de torneio
    tournament_types_list,
    tournament_type_create,
    tournament_type_edit,

    # Torneios
    season_tournaments,
    tournament_create,
    tournament_edit,
    tournament_entries_manage,
    tournament_results,

    # Jogadores
    player_login,
    player_logout,
    players_list,
    player_create,
    player_edit,
    player_register,
    player_tournaments,
    confirm_presence,

    # Blinds
    blind_structures_list,
    blind_structure_create,
    blind_structure_manage,
    
    # Diretor de torneio
    director_panel,
    director_toggle_timer,
    director_change_level,
    api_tournament_status,
)

urlpatterns = [
    # Raiz do site -> decide pra onde mandar (admin x jogador)
    path("", home_redirect, name="home_redirect"),

    # Painel do admin
    path("painel/", painel_home, name="painel_home"),

    # Atalho /login/ (usado por next=? ou links antigos) -> login do jogador
    path(
        "login/",
        RedirectView.as_view(pattern_name="player_login", permanent=False),
        name="login_redirect",
    ),

    # Ranking público
    path("ranking/<int:season_id>/", ranking_season, name="ranking_season"),
    path("tv/ranking/<int:season_id>/", tv_ranking_season, name="tv_ranking_season"),

    # Temporadas (admin)
    path("temporadas/", seasons_list, name="seasons_list"),
    path("temporadas/nova/", season_create, name="season_create"),
    path("temporadas/editar/<int:season_id>/", season_edit, name="season_edit"),
    path(
        "temporadas/<int:season_id>/pontos-iniciais/",
        season_initial_points,
        name="season_initial_points",
    ),
    path(
        "temporadas/<int:season_id>/jogador/<int:player_id>/evolucao/",
        player_progress_season,
        name="player_progress_season",
    ),

    # Tipos de torneio (admin)
    path("tipos-torneio/", tournament_types_list, name="tournament_types_list"),
    path("tipos-torneio/novo/", tournament_type_create, name="tournament_type_create"),
    path(
        "tipos-torneio/editar/<int:tipo_id>/",
        tournament_type_edit,
        name="tournament_type_edit",
    ),

    # Torneios (admin)
    path(
        "season/<int:season_id>/torneios/",
        season_tournaments,
        name="season_tournaments",
    ),
    path(
        "season/<int:season_id>/torneios/novo/",
        tournament_create,
        name="tournament_create",
    ),
    path(
        "torneio/<int:tournament_id>/editar/",
        tournament_edit,
        name="tournament_edit",
    ),
    path(
        "torneio/<int:tournament_id>/jogadores/",
        tournament_entries_manage,
        name="tournament_entries_manage",
    ),
    path(
        "torneio/<int:tournament_id>/lancamento/",
        tournament_results,
        name="tournament_results",
    ),

    # Jogadores (site público / portal)
    path("jogador/login/", player_login, name="player_login"),
    path("jogador/logout/", player_logout, name="player_logout"),
    path("jogadores/", players_list, name="players_list"),
    path("jogadores/novo/", player_create, name="player_create"),
    path("jogadores/editar/<int:player_id>/", player_edit, name="player_edit"),

    path("jogador/cadastro/", player_register, name="player_register"),
    path("jogador/torneios/", player_tournaments, name="player_tournaments"),
    path(
        "jogador/confirmar/<int:tournament_id>/",
        confirm_presence,
        name="confirm_presence",
    ),

    # --- BLINDS ---
    path("blinds/", blind_structures_list, name="blind_structures_list"),
    path("blinds/nova/", blind_structure_create, name="blind_structure_create"),
    path("blinds/<int:structure_id>/gerenciar/", blind_structure_manage, name="blind_structure_manage"),

# PAINEL DO DIRETOR
    path("torneio/<int:tournament_id>/diretor/", director_panel, name="director_panel"),
    path("torneio/<int:tournament_id>/timer/toggle/", director_toggle_timer, name="director_toggle_timer"),
    path("torneio/<int:tournament_id>/nivel/<str:direction>/", director_change_level, name="director_change_level"),

# --- API (Dados para o Telão JS) ---
    path("api/torneio/<int:tournament_id>/status/", api_tournament_status, name="api_tournament_status"),
]
