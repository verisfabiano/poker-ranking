from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import Player, Season, Tournament, TournamentEntry, TournamentResult, SeasonInitialPoints, PlayerStatistics, Tenant
from .auth import player_required, admin_required
from .ranking import tenant_required
from .season import calcular_pontos_posicao, _build_ranking_for_season
from django.utils import timezone
from django.db.models import Sum, Q, F, Case, When, Count, Max, DecimalField, IntegerField

# --- HOME DO JOGADOR ---

@login_required
def player_home(request):
    """Dashboard inicial do jogador - mostra temporadas ativas e próximos torneios"""
    
    # Garantir que o tenant está configurado
    if not hasattr(request, 'tenant') or not request.tenant:
        from ..models import TenantUser
        tenant_user = TenantUser.objects.select_related('tenant').filter(
            user=request.user, tenant__ativo=True
        ).first()
        
        if tenant_user:
            request.tenant = tenant_user.tenant
        else:
            return redirect('player_login')
    
    try:
        player = Player.objects.get(user=request.user, tenant=request.tenant)
    except Player.DoesNotExist:
        return redirect("player_register")
    
    # Temporadas ativas
    seasons_ativas = Season.objects.filter(tenant=request.tenant, ativo=True).order_by("-data_inicio")
    
    # Obter a season ativa mais recente para disponibilizar no botão "Ranking Avançado"
    current_season = seasons_ativas.first()
    
    # Próximos torneios (próximos 7 dias)
    data_agora = timezone.now()
    proximos_torneios = Tournament.objects.filter(
        tenant=request.tenant,
        data__gte=data_agora,
        data__lte=data_agora + timezone.timedelta(days=7),
        status="AGENDADO"
    ).order_by("data")[:5]
    
    # Torneios que o jogador já se inscreveu
    minhas_inscricoes = TournamentEntry.objects.filter(
        player=player,
        tournament__tenant=request.tenant
    ).select_related('tournament', 'tournament__season').order_by('-tournament__data')[:5]
    
    # ============== PHASE 1: INFORMAÇÕES FINANCEIRAS ==============
    
    # Calcular estatísticas financeiras (gasto total, ganho total, saldo, ROI)
    # Apenas torneios ENCERRADOS devem contar
    entries_finalizadas = TournamentEntry.objects.filter(
        player=player,
        tournament__tenant=request.tenant,
        tournament__status="ENCERRADO"  # Apenas torneios encerrados
    )
    
    entries_todas = TournamentEntry.objects.filter(
        player=player,
        tournament__tenant=request.tenant
    )
    
    # Gasto total (apenas buy-in da inscrição em torneios finalizados)
    # Obs: Rebuy e addon seriam rastreados em PlayerProductPurchase quando implementado
    gasto_total = entries_finalizadas.aggregate(
        total=Sum('tournament__buyin', default=0)
    )['total'] or 0
    
    # Ganho total (prêmios em torneios encerrados)
    ganho_total = TournamentResult.objects.filter(
        player=player,
        tournament__tenant=request.tenant,
        tournament__status="ENCERRADO"  # Apenas torneios encerrados
    ).aggregate(Sum('premiacao_recebida', default=0))['premiacao_recebida__sum'] or 0
    
    # Saldo líquido
    saldo_liquido = ganho_total - gasto_total
    
    # ROI
    roi = ((saldo_liquido / gasto_total) * 100) if gasto_total > 0 else 0
    
    # ============== PHASE 1: ESTATÍSTICAS GERAIS ==============
    
    # Contar participações (apenas torneios encerrados)
    total_torneios = entries_finalizadas.count()
    # Rebuy e addon serão contados de PlayerProductPurchase quando implementado
    total_rebuys = 0
    total_addons = 0
    
    # Colocações (apenas torneios encerrados)
    results_todas = TournamentResult.objects.filter(
        player=player,
        tournament__tenant=request.tenant,
        tournament__status="ENCERRADO"  # Apenas torneios encerrados
    )
    
    primeiro_lugar = results_todas.filter(posicao=1).count()
    top_3 = results_todas.filter(posicao__lte=3).count()
    top_10 = results_todas.filter(posicao__lte=10).count()
    
    # Taxa ITM (in the money - com prêmio)
    com_premio = results_todas.filter(premiacao_recebida__gt=0).count()
    taxa_itm = (com_premio / total_torneios * 100) if total_torneios > 0 else 0
    
    # ============== PHASE 1: POSIÇÃO NO RANKING ==============
    
    # Buscar ranking atual (primeira temporada ativa)
    temporada_ativa = seasons_ativas.first()
    ranking_position = None
    total_ranking_players = 0
    pontos_atuais = 0
    
    if temporada_ativa:
        # Recalcular ranking para temporada ativa (para atualizar dados)
        from .ranking import _calcular_e_atualizar_stats
        _calcular_e_atualizar_stats(temporada_ativa, player, request.tenant)
        
        # Buscar posição do jogador no ranking
        # Apenas jogadores com pelo menos 1 ponto ou 1 participação
        ranking = PlayerStatistics.objects.filter(
            season=temporada_ativa,
            tenant=request.tenant,
            pontos_totais__gt=0  # Apenas jogadores com pontos
        ).select_related('player').order_by('-pontos_totais', '-vitórias', '-top_3')
        
        total_ranking_players = ranking.count()
        
        for idx, stat in enumerate(ranking, 1):
            if stat.player_id == player.id:
                ranking_position = idx
                pontos_atuais = stat.pontos_totais
                break
    
    # ============== PHASE 1: ÚLTIMOS RESULTADOS ==============
    
    ultimos_resultados = TournamentResult.objects.filter(
        player=player,
        tournament__tenant=request.tenant
    ).select_related(
        'tournament',
        'tournament__tipo'
    ).order_by('-tournament__data')[:10]
    
    context = {
        'player': player,
        'seasons_ativas': seasons_ativas,
        'proximos_torneios': proximos_torneios,
        'minhas_inscricoes': minhas_inscricoes,
        
        # Financial summary
        'gasto_total': gasto_total,
        'ganho_total': ganho_total,
        'saldo_liquido': saldo_liquido,
        'roi': roi,
        
        # Statistics
        'total_torneios': total_torneios,
        'total_rebuys': total_rebuys,
        'total_addons': total_addons,
        'primeiro_lugar': primeiro_lugar,
        'top_3': top_3,
        'top_10': top_10,
        'taxa_itm': taxa_itm,
        
        # Ranking position
        'ranking_position': ranking_position,
        'total_ranking_players': total_ranking_players,
        'pontos_atuais': pontos_atuais,
        'temporada_ativa': temporada_ativa,
        
        # Season for ranking button
        'season': current_season,
        
        # Recent results
        'ultimos_resultados': ultimos_resultados,
    }
    return render(request, 'player_home.html', context)


# --- SELEÇÃO DE TENANT PARA CADASTRO ---

def select_tenant_register(request):
    """Página de seleção de tenant antes do cadastro de jogador"""
    tenants = Tenant.objects.filter(ativo=True)
    
    if request.method == "POST":
        tenant_id = request.POST.get("tenant_id")
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, ativo=True)
                # Salva o tenant na sessão
                request.session['selected_tenant_id'] = tenant.id
                # Redireciona para o cadastro
                return redirect('player_register')
            except Tenant.DoesNotExist:
                pass
    
    return render(request, 'select_tenant_register.html', {'tenants': tenants})


# --- LISTA DE JOGADORES (PÚBLICA) ---

def players_list(request):
    """Lista todos os jogadores"""
    players = Player.objects.filter(tenant=request.tenant).order_by("nome")
    return render(request, "players_list.html", {"players": players})


# --- CRUD DE JOGADOR ---

def player_create(request):
    """Criar novo jogador (registro)"""
    # Verificar se tenant foi definido
    if not request.tenant:
        return redirect('select_tenant_register')
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        apelido = request.POST.get("apelido")
        email = request.POST.get("email", "").strip()
        
        # Validar: precisa do nome, email é opcional
        if not nome:
            return render(request, "player_form.html", {
                "player": None,
                "error": "Nome é obrigatório",
                "tenant": request.tenant
            })
        
        # Se email vazio, deixar como None/blank
        email = email if email else None
        
        try:
            Player.objects.create(
                nome=nome, 
                apelido=apelido or None,
                email=email, 
                tenant=request.tenant
            )
            return redirect("players_list")
        except Exception as e:
            return render(request, "player_form.html", {
                "player": None,
                "error": f"Erro ao criar jogador: {str(e)}",
                "tenant": request.tenant
            })
    
    return render(request, "player_form.html", {"player": None, "tenant": request.tenant})


def player_edit(request, player_id):
    """Editar dados do jogador"""
    player = get_object_or_404(Player, id=player_id, tenant=request.tenant)
    
    # Só jogador ou admin pode editar
    if request.user != player.user and not request.user.is_staff:
        return redirect("players_list")
    
    if request.method == "POST":
        player.nome = request.POST.get("nome", player.nome)
        player.apelido = request.POST.get("apelido", player.apelido)
        player.cpf = request.POST.get("cpf", player.cpf) or None
        player.telefone = request.POST.get("telefone", player.telefone) or None
        
        # Processar upload de foto
        if 'foto' in request.FILES:
            player.foto = request.FILES['foto']
        
        # Verificar se deve criar/manter usuário
        criar_usuario = request.POST.get("criar_usuario") == "on"  # checkbox
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        
        if criar_usuario and username and email:
            # Criar ou atualizar usuário
            if player.user:
                # Atualizar usuário existente
                player.user.username = username
                player.user.email = email
                player.user.save()
            else:
                # Criar novo usuário
                try:
                    user = User.objects.create_user(username=username, email=email)
                    player.user = user
                except:
                    # Username já existe
                    return render(request, "player_form.html", {
                        "player": player,
                        "error": "Username já está em uso"
                    })
        elif not criar_usuario and player.user:
            # Se está desmarcado e tinha usuário, remover a ligação
            # Nota: Podemos manter o User no banco por segurança de histórico
            # ou deletar. Vou deixar como está por enquanto
            pass
        
        player.save()
        return redirect("players_list")
    
    return render(request, "player_form.html", {"player": player})


def player_profile(request):
    """Perfil do jogador logado (não precisa de ID)"""
    # Buscar o jogador associado ao usuário logado
    player = get_object_or_404(Player, user=request.user, tenant=request.tenant)
    
    if request.method == "POST":
        player.nome = request.POST.get("nome", player.nome)
        player.apelido = request.POST.get("apelido", player.apelido)
        player.cpf = request.POST.get("cpf", player.cpf) or None
        player.telefone = request.POST.get("telefone", player.telefone) or None
        
        # Processar upload de foto
        if 'foto' in request.FILES:
            player.foto = request.FILES['foto']
        
        player.save()
        
        # Redirecionar com mensagem de sucesso
        return redirect("player_profile")
    
    return render(request, "player_profile.html", {"player": player})


def player_register(request):
    """Registro de novo jogador"""
    # Se o tenant não foi identificado pelo middleware,
    # tenta usar o da sessão (vem da seleção de clube)
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        tenant_id = request.session.get('selected_tenant_id')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, ativo=True)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                return redirect('select_tenant_register')
        else:
            return redirect('select_tenant_register')
    
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        apelido = request.POST.get("apelido", "").strip()
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()
        
        # Validações
        error = None
        if not nome:
            error = "Nome é obrigatório"
        elif not email:
            error = "E-mail é obrigatório"
        elif not senha:
            error = "Senha é obrigatória"
        elif len(senha) < 6:
            error = "Senha deve ter pelo menos 6 caracteres"
        elif User.objects.filter(username=email).exists():
            error = "Este e-mail já está registrado"
        
        if error:
            return render(request, "player_register.html", {
                "tenant": tenant,
                "error": error,
                "nome": nome,
                "apelido": apelido,
                "email": email
            })
        
        try:
            # 1. Criar usuário Django
            user = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
                first_name=nome
            )
            
            # 2. Criar Player vinculado ao usuário
            player = Player.objects.create(
                nome=nome,
                apelido=apelido,
                email=email,
                user=user,
                tenant=tenant
            )
            
            # 3. Criar TenantUser para vincular usuário ao tenant (necessário para middleware)
            from ..models import TenantUser
            TenantUser.objects.create(user=user, tenant=tenant)
            
            # Limpa a sessão
            if 'selected_tenant_id' in request.session:
                del request.session['selected_tenant_id']
            
            # Login automático após cadastro
            from django.contrib.auth import login
            login(request, user)
            
            return redirect("player_home")
        
        except Exception as e:
            return render(request, "player_register.html", {
                "tenant": tenant,
                "error": f"Erro ao registrar: {str(e)}",
                "nome": nome,
                "apelido": apelido,
                "email": email
            })
    
    return render(request, "player_register.html", {"tenant": tenant})


# --- TORNEIOS DO JOGADOR ---

def player_tournaments(request):
    """Listar torneios disponíveis para o jogador se inscrever"""
    try:
        player = Player.objects.get(user=request.user, tenant=request.tenant)
    except Player.DoesNotExist:
        return redirect("player_register")
    
    # Todos os torneios agendados do tenant
    todos_torneios = Tournament.objects.filter(
        tenant=request.tenant,
        status="AGENDADO"
    ).select_related('season', 'tipo').order_by("data")
    
    # Minhas inscrições
    minhas_inscricoes = TournamentEntry.objects.filter(
        player=player,
        tournament__tenant=request.tenant
    ).values_list('tournament_id', flat=True)
    
    # Construir lista de torneios com status
    torneios = []
    for t in todos_torneios:
        inscrito = t.id in minhas_inscricoes
        confirmado = TournamentEntry.objects.filter(
            tournament=t, player=player, confirmado_pelo_admin=True
        ).exists() if inscrito else False
        
        torneios.append({
            'torneio': t,
            'inscrito': inscrito,
            'confirmado': confirmado
        })
    
    context = {
        'player': player,
        'torneios': torneios,
    }
    return render(request, "player_tournaments.html", context)


def confirm_presence(request, tournament_id):
    """Jogador confirma presença em um torneio"""
    tournament = get_object_or_404(Tournament, id=tournament_id, tenant=request.tenant)
    
    try:
        player = Player.objects.get(user=request.user, tenant=request.tenant)
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

def player_progress_season(request, season_id, player_id):
    """
    Mostrar evolução do jogador em uma temporada (PUBLIC VIEW).
    
    Qualquer pessoa pode acessar esta página, mas os dados retornados
    serão os da season/player solicitados.
    """
    # Se o usuário está autenticado, usar seu tenant como filtro adicional
    # Caso contrário, aceitar qualquer season/player válido
    if request.user.is_authenticated and hasattr(request, 'tenant') and request.tenant:
        season = Season.objects.filter(id=season_id, tenant=request.tenant).first()
        player = Player.objects.filter(id=player_id, tenant=request.tenant).first()
    else:
        # Para usuário não autenticado, busca sem restrição de tenant
        season = Season.objects.filter(id=season_id).first()
        player = Player.objects.filter(id=player_id).first()
    
    # Validar se season e player foram encontrados
    if not season:
        from django.contrib import messages
        messages.error(request, f"A temporada solicitada (ID: {season_id}) não foi encontrada.")
        return redirect("seasons_list")
    
    if not player:
        from django.contrib import messages
        messages.error(request, f"O jogador solicitado (ID: {player_id}) não foi encontrado.")
        return redirect("seasons_list")
    
    # Para determinar o tenant, usar o que foi obtido da season
    tenant = season.tenant
    
    # Pontos iniciais
    pontos_iniciais = SeasonInitialPoints.objects.filter(
        season=season,
        player=player,
        tenant=tenant
    ).first()
    pontos_iniciais_valor = pontos_iniciais.pontos if pontos_iniciais else 0
    
    # Torneios participados
    entries = TournamentEntry.objects.filter(
        tournament__season=season,
        tournament__tenant=tenant,
        player=player,
        confirmado_pelo_admin=True
    ).select_related('tournament').order_by('tournament__data')
    
    # Montar progresso
    progresso = []
    acumulado = pontos_iniciais_valor
    
    # Adicionar entrada de pontos iniciais
    if pontos_iniciais_valor > 0:
        progresso.append({
            'tipo': 'iniciais',
            'descricao': 'Ajuste de pontos iniciais',
            'data': season.data_inicio,
            'pontos_rodada': pontos_iniciais_valor,
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
                'torneio': entry.tournament,  # Passar o objeto do torneio completo
                'data': entry.tournament.data,
                'posicao': result.posicao,
                'pontos_rodada': int(pontos),
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


# --- CADASTRO RÁPIDO DE JOGADOR (AJAX) ---

@admin_required
def player_create_quick(request):
    """Criar novo jogador rapidamente (via AJAX para uso em tournament_entries)
    - Se username e email: cria Player com User (pode fazer login)
    - Se ambos em branco: cria apenas Player (jogador de passagem)
    """
    import json
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        nome = (data.get('nome') or '').strip()
        apelido = (data.get('apelido') or '').strip() or None
        cpf = (data.get('cpf') or '').strip() or None
        telefone = (data.get('telefone') or '').strip() or None
        username = (data.get('username') or '').strip() or None
        email = (data.get('email') or '').strip() or None
        
        # Validações
        if not nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome é obrigatório'
            }, status=400)
        
        # Se um é preenchido, ambos devem ser preenchidos
        if bool(username) != bool(email):
            return JsonResponse({
                'success': False,
                'error': 'Para criar usuário, preencha tanto username quanto email'
            }, status=400)
        
        # Verificar duplicatas apenas se vai criar usuário
        if username:
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Username "{username}" já está em uso'
                }, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Email "{email}" já está cadastrado'
                }, status=400)
        
        # Criar User Django apenas se username foi fornecido
        user = None
        if username:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=nome.split()[0] if nome else ''
            )
        
        # Criar Player com todos os campos
        player = Player.objects.create(
            user=user,
            nome=nome,
            apelido=apelido,
            cpf=cpf,
            telefone=telefone,
            tenant=request.tenant
        )
        
        return JsonResponse({
            'success': True,
            'player_id': player.id,
            'player_nome': player.nome,
            'player_apelido': player.apelido,
            'tem_usuario': bool(user),
            'message': f'Jogador {nome} criado com sucesso'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        print(f'Erro ao criar jogador: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': f'Erro ao criar jogador: {str(e)}'
        }, status=500)


# --- GESTÃO DO CLUBE ---

@login_required
def club_edit(request):
    """Editar informações do clube (apenas para staff/admin do club)"""
    # Verificar permissão
    if not request.user.is_staff:
        return redirect("player_home")
    
    tenant = request.tenant
    
    if request.method == "POST":
        # Atualizar informações básicas
        tenant.descricao = request.POST.get("descricao", tenant.descricao)
        
        # Contato
        tenant.club_email = request.POST.get("club_email", tenant.club_email)
        tenant.club_phone = request.POST.get("club_phone", tenant.club_phone)
        tenant.club_cnpj = request.POST.get("club_cnpj", tenant.club_cnpj)
        tenant.club_website = request.POST.get("club_website", tenant.club_website)
        
        # Endereço
        tenant.address_cep = request.POST.get("address_cep", tenant.address_cep)
        tenant.address_street = request.POST.get("address_street", tenant.address_street)
        tenant.address_number = request.POST.get("address_number", tenant.address_number)
        tenant.address_complement = request.POST.get("address_complement", tenant.address_complement)
        tenant.address_neighborhood = request.POST.get("address_neighborhood", tenant.address_neighborhood)
        tenant.address_city = request.POST.get("address_city", tenant.address_city)
        tenant.address_state = request.POST.get("address_state", tenant.address_state)
        
        # Admin
        tenant.admin_full_name = request.POST.get("admin_full_name", tenant.admin_full_name)
        tenant.admin_phone = request.POST.get("admin_phone", tenant.admin_phone)
        tenant.admin_cpf = request.POST.get("admin_cpf", tenant.admin_cpf)
        tenant.admin_role = request.POST.get("admin_role", tenant.admin_role)
        
        # Logo
        if 'logo' in request.FILES:
            tenant.logo = request.FILES['logo']
        
        tenant.save()
        
        return redirect("club_edit")
    
    return render(request, "club_edit.html", {"tenant": tenant})