from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Player, Season, Tournament, TournamentEntry, TournamentResult, SeasonInitialPoints
from .auth import player_required, admin_required
from .season import calcular_pontos_posicao, _build_ranking_for_season
from django.utils import timezone

# --- HOME DO JOGADOR ---

@player_required
def player_home(request):
    """Dashboard inicial do jogador - mostra temporadas ativas e próximos torneios"""
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return redirect("player_register")
    
    # Temporadas ativas
    seasons_ativas = Season.objects.filter(ativo=True).order_by("-data_inicio")
    
    # Próximos torneios (próximos 7 dias)
    data_agora = timezone.now()
    proximos_torneios = Tournament.objects.filter(
        data__gte=data_agora,
        data__lte=data_agora + timezone.timedelta(days=7),
        status="AGENDADO"
    ).order_by("data")[:5]
    
    # Torneios que o jogador já se inscreveu
    minhas_inscricoes = TournamentEntry.objects.filter(
        player=player
    ).select_related('tournament', 'tournament__season').order_by('-tournament__data')[:5]
    
    context = {
        'player': player,
        'seasons_ativas': seasons_ativas,
        'proximos_torneios': proximos_torneios,
        'minhas_inscricoes': minhas_inscricoes,
    }
    return render(request, 'player_home.html', context)


# --- LISTA DE JOGADORES (PÚBLICA) ---

@login_required
def players_list(request):
    """Lista todos os jogadores"""
    players = Player.objects.all().order_by("nome")
    return render(request, "players_list.html", {"players": players})


# --- CRUD DE JOGADOR ---

@login_required
def player_create(request):
    """Criar novo jogador (registro)"""
    if request.method == "POST":
        nome = request.POST.get("nome")
        apelido = request.POST.get("apelido")
        email = request.POST.get("email")
        
        if nome and email:
            Player.objects.create(nome=nome, apelido=apelido, email=email)
            return redirect("players_list")
    
    return render(request, "player_form.html", {"player": None})


@login_required
def player_edit(request, player_id):
    """Editar dados do jogador"""
    player = get_object_or_404(Player, id=player_id)
    
    # Só jogador ou admin pode editar
    if request.user != player.user and not request.user.is_staff:
        return redirect("players_list")
    
    if request.method == "POST":
        player.nome = request.POST.get("nome", player.nome)
        player.apelido = request.POST.get("apelido", player.apelido)
        player.email = request.POST.get("email", player.email)
        player.save()
        return redirect("players_list")
    
    return render(request, "player_form.html", {"player": player})


@login_required
def player_register(request):
    """Registro de novo jogador"""
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        apelido = request.POST.get("apelido", "").strip()
        email = request.POST.get("email", "").strip()
        
        if nome and email:
            player = Player.objects.create(
                nome=nome,
                apelido=apelido,
                email=email,
                user=request.user
            )
            return redirect("player_home")
    
    return render(request, "player_register.html")


# --- TORNEIOS DO JOGADOR ---

@player_required
def player_tournaments(request):
    """Listar torneios disponíveis para o jogador se inscrever"""
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return redirect("player_register")
    
    # Torneios agendados onde jogador NÃO está inscrito
    minha_inscricoes = TournamentEntry.objects.filter(
        player=player
    ).values_list('tournament_id', flat=True)
    
    torneios_disponiveis = Tournament.objects.filter(
        status="AGENDADO"
    ).exclude(id__in=minha_inscricoes).order_by("data")
    
    # Minhas inscrições confirmadas
    minhas_confirmadas = TournamentEntry.objects.filter(
        player=player,
        confirmado_pelo_admin=True
    ).select_related('tournament', 'tournament__season').order_by('-tournament__data')
    
    # Minhas inscrições pendentes
    minhas_pendentes = TournamentEntry.objects.filter(
        player=player,
        confirmado_pelo_admin=False
    ).select_related('tournament', 'tournament__season').order_by('-tournament__data')
    
    context = {
        'player': player,
        'torneios_disponiveis': torneios_disponiveis,
        'minhas_confirmadas': minhas_confirmadas,
        'minhas_pendentes': minhas_pendentes,
    }
    return render(request, "player_tournaments.html", context)


@player_required
def confirm_presence(request, tournament_id):
    """Jogador confirma presença em um torneio"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return redirect("player_register")
    
    # Verificar se já está inscrito
    entry, created = TournamentEntry.objects.get_or_create(
        tournament=tournament,
        player=player
    )
    
    if created:
        entry.confirmou_presenca = True
        entry.save()
    
    return redirect("player_tournaments")


# --- RANKING DO JOGADOR ---

@login_required
def player_progress_season(request, season_id, player_id):
    """Mostrar evolução do jogador em uma temporada"""
    season = get_object_or_404(Season, id=season_id)
    player = get_object_or_404(Player, id=player_id)
    
    # Pontos iniciais
    pontos_iniciais = SeasonInitialPoints.objects.filter(
        season=season,
        player=player
    ).first()
    pontos_iniciais_valor = pontos_iniciais.pontos if pontos_iniciais else 0
    
    # Torneios participados
    entries = TournamentEntry.objects.filter(
        tournament__season=season,
        player=player,
        confirmado_pelo_admin=True
    ).select_related('tournament').order_by('tournament__data')
    
    # Montar progresso
    progresso = []
    acumulado = pontos_iniciais_valor
    
    # Adicionar entrada de pontos iniciais
    if pontos_iniciais_valor > 0:
        progresso.append({
            'tipo': 'ajuste',
            'descricao': 'Ajuste de pontos iniciais',
            'data': season.data_inicio,
            'pontos': pontos_iniciais_valor,
            'acumulado': acumulado,
        })
    
    # Adicionar resultados de torneios
    for entry in entries:
        result = TournamentResult.objects.filter(
            tournament=entry.tournament,
            player=player
        ).first()
        
        if result and result.posicao:
            # Calcular pontos desta posição
            tabela_fixa = season.get_tabela_pontos_fixos() if season.tipo_calculo == 'FIXO' else None
            pontos = calcular_pontos_posicao(
                result.posicao,
                entry.tournament.total_jogadores or 5,
                entry.tournament.buyin,
                1,
                tabela_fixa
            )
            
            acumulado += int(pontos)
            
            progresso.append({
                'tipo': 'torneio',
                'descricao': entry.tournament.nome,
                'data': entry.tournament.data,
                'posicao': result.posicao,
                'pontos': int(pontos),
                'acumulado': acumulado,
            })
    
    context = {
        'season': season,
        'player': player,
        'progresso': progresso,
        'pontos_iniciais': pontos_iniciais_valor,
        'total_final': acumulado,
    }
    return render(request, "player_progress.html", context)