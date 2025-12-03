from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import (
    Season,
    TournamentType,
    Tournament,
    TournamentEntry,
    TournamentResult,
    Player,
    SeasonInitialPoints,
)

User = get_user_model()


# ============================================================
#  PERMISSÕES
# ============================================================

def is_admin(user):
    """
    Admin é qualquer usuário autenticado com is_staff ou is_superuser.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# se não for admin, mandamos para a tela de login do jogador mesmo
admin_required = user_passes_test(is_admin, login_url="player_login")


# ============================================================
#  FUNÇÃO AUXILIAR – RANKING DA TEMPORADA
# ============================================================

def _build_ranking_for_season(season):
    """
    Monta o ranking da temporada com:
    - pontos iniciais
    - pontos de torneios (pontos_finais)
    - pontos de participação
    Também calcula:
    - posição (rank)
    - flag de empate em pontos
    """

    # 1) Pontos de resultados de torneios
    resultados = (
        TournamentResult.objects
        .filter(tournament__season=season)
        .values("player__id", "player__nome", "player__apelido")
        .annotate(total_resultado=Sum("pontos_finais"))
    )

    # 2) Pontos de participação
    participacoes = (
        TournamentEntry.objects
        .filter(tournament__season=season)
        .values("player__id")
        .annotate(total_participacao=Sum("pontos_participacao"))
    )

    # 3) Pontos iniciais (migração / bônus)
    iniciais = (
        SeasonInitialPoints.objects
        .filter(season=season)
        .values("player__id", "player__nome", "player__apelido")
        .annotate(total_iniciais=Sum("pontos_iniciais"))
    )

    # ---- junta tudo num dicionário por player_id ----
    ranking_dict = {}

    # Resultados de torneio
    for r in resultados:
        pid = r["player__id"]
        ranking_dict[pid] = {
            "nome": r["player__apelido"] or r["player__nome"],
            "pontos_resultado": r["total_resultado"] or 0,
            "pontos_participacao": 0,
            "pontos_iniciais": 0,
        }

    # Participação
    for p in participacoes:
        pid = p["player__id"]
        if pid in ranking_dict:
            ranking_dict[pid]["pontos_participacao"] = p["total_participacao"]
        else:
            ranking_dict[pid] = {
                "nome": "Jogador desconhecido",
                "pontos_resultado": 0,
                "pontos_participacao": p["total_participacao"],
                "pontos_iniciais": 0,
            }

    # Pontos iniciais
    for i in iniciais:
        pid = i["player__id"]
        nome = i["player__apelido"] or i["player__nome"]
        if pid in ranking_dict:
            ranking_dict[pid]["pontos_iniciais"] = i["total_iniciais"]
        else:
            ranking_dict[pid] = {
                "nome": nome,
                "pontos_resultado": 0,
                "pontos_participacao": 0,
                "pontos_iniciais": i["total_iniciais"],
            }

    # ---- monta lista, calcula total e ordena com critério claro ----
    ranking_lista = []
    for pid, jogador in ranking_dict.items():
        total = (
            (jogador["pontos_resultado"] or 0)
            + (jogador["pontos_participacao"] or 0)
            + (jogador["pontos_iniciais"] or 0)
        )
        ranking_lista.append({
            "player_id": pid,
            "nome": jogador["nome"],
            "pontos": total,
            "pontos_resultado": jogador["pontos_resultado"] or 0,
            "pontos_participacao": jogador["pontos_participacao"] or 0,
            "pontos_iniciais": jogador["pontos_iniciais"] or 0,
        })

    # Critério de desempate:
    # 1) pontos totais desc
    # 2) mais pontos de torneios desc
    # 3) mais pontos iniciais desc
    # 4) nome alfabético
    ranking_lista.sort(
        key=lambda x: (
            -(x["pontos"]),
            -(x["pontos_resultado"]),
            -(x["pontos_iniciais"]),
            x["nome"].lower(),
        )
    )

    # ---- calcula posição (rank) e flag de empate em pontos ----
    last_pontos = None
    last_rank = 0
    index = 0

    # conta quantos têm cada pontuação (pra marcar empate visualmente)
    pontos_count = {}
    for item in ranking_lista:
        pts = item["pontos"]
        pontos_count[pts] = pontos_count.get(pts, 0) + 1

    for item in ranking_lista:
        index += 1
        if last_pontos is None or item["pontos"] < last_pontos:
            rank = index
        else:
            # mesma pontuação total => mesma posição
            rank = last_rank

        item["posicao"] = rank
        item["empatado"] = pontos_count[item["pontos"]] > 1

        last_pontos = item["pontos"]
        last_rank = rank

    return ranking_lista


# ============================================================
#  RANKING / TV (público, pode deixar sem login)
# ============================================================

def ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    ranking_lista = _build_ranking_for_season(season)

    return render(
        request,
        "ranking.html",
        {
            "season": season,
            "ranking": ranking_lista,
        },
    )


def tv_ranking_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    ranking_lista = _build_ranking_for_season(season)

    return render(
        request,
        "tv_ranking.html",
        {
            "season": season,
            "ranking": ranking_lista,
        },
    )


# ============================================================
#  EVOLUÇÃO DO JOGADOR NA TEMPORADA (pode ser público)
# ============================================================

def player_progress_season(request, season_id, player_id):
    season = get_object_or_404(Season, id=season_id)
    player = get_object_or_404(Player, id=player_id)

    sip = SeasonInitialPoints.objects.filter(
        season=season,
        player=player,
    ).first()
    pontos_iniciais = sip.pontos_iniciais if sip else 0

    torneios = (
        Tournament.objects
        .filter(season=season)
        .order_by("data")
    )

    progresso = []
    acumulado = pontos_iniciais

    if pontos_iniciais != 0:
        progresso.append({
            "tipo": "iniciais",
            "descricao": "Pontos iniciais da temporada",
            "data": None,
            "torneio": None,
            "pontos_rodada": pontos_iniciais,
            "acumulado": acumulado,
        })

    for t in torneios:
        result = TournamentResult.objects.filter(
            tournament=t,
            player=player,
        ).first()

        pts_rodada = result.pontos_finais if result else 0
        acumulado += pts_rodada
        progresso.append({
            "tipo": "torneio",
            "descricao": t.nome,
            "data": t.data,
            "torneio": t,
            "pontos_rodada": pts_rodada,
            "acumulado": acumulado,
        })

    total_final = acumulado

    return render(
        request,
        "player_progress.html",
        {
            "season": season,
            "player": player,
            "progresso": progresso,
            "pontos_iniciais": pontos_iniciais,
            "total_final": total_final,
        },
    )


# ============================================================
#  PAINEL DO ORGANIZADOR (ADMIN)
# ============================================================

@admin_required
def painel_home(request):
    seasons = Season.objects.order_by("-data_inicio")

    return render(
        request,
        "painel_home.html",
        {
            "seasons": seasons,
        },
    )


# ============================================================
#  CRUD DE TEMPORADAS (ADMIN)
# ============================================================

@admin_required
def seasons_list(request):
    seasons = Season.objects.order_by("-data_inicio")
    return render(
        request,
        "seasons_list.html",
        {"seasons": seasons},
    )


@admin_required
def season_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_inicio_str = request.POST.get("data_inicio", "").strip()
        data_fim_str = request.POST.get("data_fim", "").strip()
        ativo = request.POST.get("ativo") == "on"

        if nome and data_inicio_str and data_fim_str:
            try:
                data_inicio = date.fromisoformat(data_inicio_str)
                data_fim = date.fromisoformat(data_fim_str)
            except ValueError:
                data_inicio = date.today()
                data_fim = date.today()

            Season.objects.create(
                nome=nome,
                data_inicio=data_inicio,
                data_fim=data_fim,
                ativo=ativo,
            )

        return HttpResponseRedirect(reverse("seasons_list"))

    return render(request, "season_form.html", {"season": None})


@admin_required
def season_edit(request, season_id):
    season = get_object_or_404(Season, id=season_id)

    if request.method == "POST":
        season.nome = request.POST.get("nome", "").strip()
        data_inicio_str = request.POST.get("data_inicio", "").strip()
        data_fim_str = request.POST.get("data_fim", "").strip()
        season.ativo = request.POST.get("ativo") == "on"

        try:
            if data_inicio_str:
                season.data_inicio = date.fromisoformat(data_inicio_str)
            if data_fim_str:
                season.data_fim = date.fromisoformat(data_fim_str)
        except ValueError:
            pass

        season.save()
        return HttpResponseRedirect(reverse("seasons_list"))

    return render(
        request,
        "season_form.html",
        {"season": season},
    )


# ============================================================
#  PONTOS INICIAIS DA TEMPORADA (ADMIN)
# ============================================================

@admin_required
def season_initial_points(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    mensagem = None

    players = Player.objects.filter(ativo=True).order_by("nome")

    if request.method == "POST":
        for player in players:
            field_name = f"pontos_{player.id}"
            val_str = request.POST.get(field_name, "").strip()

            if val_str == "":
                SeasonInitialPoints.objects.filter(
                    season=season,
                    player=player,
                ).delete()
                continue

            try:
                pontos = int(val_str)
            except ValueError:
                pontos = 0

            sip, created = SeasonInitialPoints.objects.get_or_create(
                season=season,
                player=player,
                defaults={"pontos_iniciais": pontos},
            )
            if not created:
                sip.pontos_iniciais = pontos
                sip.save()

        mensagem = "Pontos iniciais salvos com sucesso."

    iniciais_map = {
        sip.player_id: sip.pontos_iniciais
        for sip in SeasonInitialPoints.objects.filter(season=season)
    }

    linhas = []
    for p in players:
        linhas.append(
            {
                "player": p,
                "pontos": iniciais_map.get(p.id, 0),
            }
        )

    return render(
        request,
        "season_initial_points.html",
        {
            "season": season,
            "linhas": linhas,
            "mensagem": mensagem,
        },
    )


# ============================================================
#  TIPOS DE TORNEIO (ADMIN)
# ============================================================

@admin_required
def tournament_types_list(request):
    tipos = TournamentType.objects.order_by("nome")
    return render(
        request,
        "tournament_types_list.html",
        {"tipos": tipos},
    )


@admin_required
def tournament_type_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        multiplicador_str = request.POST.get("multiplicador", "1").strip()
        usa_regras_padrao = request.POST.get("usa_regras_padrao") == "on"

        if not multiplicador_str:
            multiplicador_str = "1"

        try:
            multiplicador = Decimal(multiplicador_str.replace(",", "."))
        except InvalidOperation:
            multiplicador = Decimal("1")

        if nome:
            TournamentType.objects.create(
                nome=nome,
                descricao=descricao or None,
                multiplicador_pontos=multiplicador,
                usa_regras_padrao=usa_regras_padrao,
            )

        return HttpResponseRedirect(reverse("tournament_types_list"))

    return render(
        request,
        "tournament_type_form.html",
        {"tipo": None},
    )


@admin_required
def tournament_type_edit(request, tipo_id):
    tipo = get_object_or_404(TournamentType, id=tipo_id)

    if request.method == "POST":
        tipo.nome = request.POST.get("nome", "").strip()
        tipo.descricao = request.POST.get("descricao", "").strip() or None
        multiplicador_str = request.POST.get("multiplicador", "1").strip()
        tipo.usa_regras_padrao = request.POST.get("usa_regras_padrao") == "on"

        if not multiplicador_str:
            multiplicador_str = "1"

        try:
            tipo.multiplicador_pontos = Decimal(
                multiplicador_str.replace(",", ".")
            )
        except InvalidOperation:
            pass

        tipo.save()
        return HttpResponseRedirect(reverse("tournament_types_list"))

    return render(
        request,
        "tournament_type_form.html",
        {"tipo": tipo},
    )


# ============================================================
#  TORNEIOS DA TEMPORADA (ADMIN)
# ============================================================

@admin_required
def season_tournaments(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tournaments = (
        Tournament.objects
        .filter(season=season)
        .order_by("-data")
    )

    return render(
        request,
        "tournaments_list.html",
        {
            "season": season,
            "tournaments": tournaments,
        },
    )


@admin_required
def tournament_create(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    tipos = TournamentType.objects.order_by("nome")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_str = request.POST.get("data", "").strip()
        tipo_id = request.POST.get("tipo_id")
        status = request.POST.get("status", "AGENDADO")

        buy_in_str = request.POST.get("buy_in", "").strip()
        garantido_str = request.POST.get("garantido", "").strip()

        if nome and data_str and tipo_id:
            try:
                data = datetime.fromisoformat(data_str)
            except ValueError:
                data = datetime.now()

            tipo = get_object_or_404(TournamentType, id=int(tipo_id))

            buy_in = None
            garantido = None

            if buy_in_str:
                try:
                    buy_in = Decimal(buy_in_str.replace(",", "."))
                except InvalidOperation:
                    buy_in = None

            if garantido_str:
                try:
                    garantido = Decimal(garantido_str.replace(",", "."))
                except InvalidOperation:
                    garantido = None

            Tournament.objects.create(
                nome=nome,
                data=data,
                season=season,
                tipo=tipo,
                buy_in=buy_in,
                garantido=garantido,
                status=status,
            )

        return HttpResponseRedirect(
            reverse("season_tournaments", args=[season.id])
        )

    return render(
        request,
        "tournament_form.html",
        {
            "season": season,
            "tipos": tipos,
            "tournament": None,
        },
    )


@admin_required
def tournament_edit(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    tipos = TournamentType.objects.order_by("nome")

    if request.method == "POST":
        tournament.nome = request.POST.get("nome", "").strip()
        data_str = request.POST.get("data", "").strip()
        tipo_id = request.POST.get("tipo_id")
        tournament.status = request.POST.get("status", "AGENDADO")

        buy_in_str = request.POST.get("buy_in", "").strip()
        garantido_str = request.POST.get("garantido", "").strip()

        if data_str:
            try:
                tournament.data = datetime.fromisoformat(data_str)
            except ValueError:
                pass

        if tipo_id:
            tournament.tipo = get_object_or_404(TournamentType, id=int(tipo_id))

        if buy_in_str:
            try:
                tournament.buy_in = Decimal(buy_in_str.replace(",", "."))
            except InvalidOperation:
                pass
        else:
            tournament.buy_in = None

        if garantido_str:
            try:
                tournament.garantido = Decimal(garantido_str.replace(",", "."))
            except InvalidOperation:
                pass
        else:
            tournament.garantido = None

        tournament.save()
        return HttpResponseRedirect(
            reverse("season_tournaments", args=[season.id])
        )

    data_str = tournament.data.strftime("%Y-%m-%dT%H:%M")

    return render(
        request,
        "tournament_form.html",
        {
            "season": season,
            "tipos": tipos,
            "tournament": tournament,
            "data_str": data_str,
        },
    )


# ============================================================
#  JOGADORES – CRUD (ADMIN)
# ============================================================

@admin_required
def players_list(request):
    players = Player.objects.order_by("nome")

    return render(
        request,
        "players_list.html",
        {
            "players": players,
        },
    )


@admin_required
def player_create(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        apelido = request.POST.get("apelido", "").strip()
        cpf = request.POST.get("cpf", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        ativo = request.POST.get("ativo") == "on"

        if nome:
            Player.objects.create(
                nome=nome,
                apelido=apelido or None,
                cpf=cpf or None,
                telefone=telefone or None,
                ativo=ativo,
            )

        return HttpResponseRedirect(reverse("players_list"))

    return render(request, "player_form.html", {"player": None})


@admin_required
def player_edit(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":
        player.nome = request.POST.get("nome", "").strip()
        player.apelido = request.POST.get("apelido", "").strip() or None
        player.cpf = request.POST.get("cpf", "").strip() or None
        player.telefone = request.POST.get("telefone", "").strip() or None
        player.ativo = request.POST.get("ativo") == "on"
        player.save()

        return HttpResponseRedirect(reverse("players_list"))

    return render(
        request,
        "player_form.html",
        {
            "player": player,
        },
    )


# ============================================================
#  FLUXO DO JOGADOR (SITE PÚBLICO)
# ============================================================

def player_login(request):
    """
    Login unificado para jogador e admin.

    - Campo "E-mail" aceita tanto o e-mail quanto o username.
    - Se o usuário for admin (is_staff ou is_superuser), manda para o painel.
    - Se for jogador normal, manda para a tela de torneios.
    """
    mensagem = None

    if request.method == "POST":
        login_input = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()

        user = None

        if login_input:
            # 1) tenta achar usuário pelo e-mail
            user_obj = User.objects.filter(email__iexact=login_input).first()

            if user_obj:
                # autentica usando o username real desse usuário
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=senha,
                )
            else:
                # 2) se não achou por e-mail, tenta usar o que foi digitado como username
                user = authenticate(
                    request,
                    username=login_input,
                    password=senha,
                )

        if user is not None:
            login(request, user)

            # se for admin, vai para o painel; senão, vai para os torneios do jogador
            if is_admin(user):
                return HttpResponseRedirect(reverse("painel_home"))
            else:
                return HttpResponseRedirect(reverse("player_tournaments"))
        else:
            mensagem = "E-mail ou senha inválidos."

    return render(request, "player_login.html", {"mensagem": mensagem})



def player_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("player_login"))


def player_register(request):
    mensagem = None

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        apelido = request.POST.get("apelido", "").strip()
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "").strip()

        if not (nome and email and senha):
            mensagem = "Preencha nome, e-mail e senha."
        elif User.objects.filter(username=email).exists():
            mensagem = "Este e-mail já está cadastrado."
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
            )

            Player.objects.create(
                user=user,
                nome=nome,
                apelido=apelido or None,
                ativo=True,
            )

            login(request, user)
            return HttpResponseRedirect(reverse("player_tournaments"))

    return render(request, "player_register.html", {"mensagem": mensagem})


@login_required
def player_tournaments(request):
    player = get_object_or_404(Player, user=request.user)

    torneios = Tournament.objects.filter(status="AGENDADO").order_by("data")

    torneios_com_status = []
    for t in torneios:
        entry = TournamentEntry.objects.filter(tournament=t, player=player).first()
        torneios_com_status.append({
            "torneio": t,
            "inscrito": bool(entry),
            "confirmado": entry.confirmado_pelo_admin if entry else False,
        })

    return render(
        request,
        "player_tournaments.html",
        {"torneios": torneios_com_status},
    )


@login_required
def confirm_presence(request, tournament_id):
    player = get_object_or_404(Player, user=request.user)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.status != "AGENDADO":
        return HttpResponseRedirect(reverse("player_tournaments"))

    entry, created = TournamentEntry.objects.get_or_create(
        tournament=tournament,
        player=player,
        defaults={
            "confirmou_presenca": True,
            "confirmado_pelo_admin": False,
        },
    )

    if not created:
        entry.confirmou_presenca = True
        entry.save()

    return HttpResponseRedirect(reverse("player_tournaments"))


# ============================================================
#  JOGADORES NO TORNEIO (ADMIN)
# ============================================================

@admin_required
def tournament_entries_manage(request, tournament_id):
    """
    Central do admin para gerenciar inscrições e presença do torneio.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    mensagem = None
    mensagem_erro = None

    edicao_bloqueada = tournament.status in ("EM_ANDAMENTO", "FINALIZADO")

    if request.method == "POST":
        if edicao_bloqueada:
            return HttpResponseRedirect(
                reverse("tournament_entries_manage", args=[tournament.id]) + "?erro_status=1"
            )

        if "add_player" in request.POST:
            player_id_str = request.POST.get("novo_player_id")
            if player_id_str:
                try:
                    player = Player.objects.filter(
                        id=int(player_id_str),
                        ativo=True,
                    ).first()
                    if player:
                        TournamentEntry.objects.get_or_create(
                            tournament=tournament,
                            player=player,
                        )
                except ValueError:
                    pass

            return HttpResponseRedirect(
                reverse("tournament_entries_manage", args=[tournament.id]) + "?ok=1"
            )

        if "remove_selected" in request.POST:
            ids = request.POST.getlist("remover_entry_id")

            entries_qs = TournamentEntry.objects.filter(
                tournament=tournament,
                id__in=ids,
            )
            player_ids = list(entries_qs.values_list("player_id", flat=True))

            if player_ids:
                TournamentResult.objects.filter(
                    tournament=tournament,
                    player_id__in=player_ids,
                ).delete()

            entries_qs.delete()

            return HttpResponseRedirect(
                reverse("tournament_entries_manage", args=[tournament.id]) + "?ok=1"
            )

        if "save_admin_confirm" in request.POST:
            entries = TournamentEntry.objects.filter(tournament=tournament)
            for entry in entries:
                field_name = f"conf_admin_{entry.id}"
                entry.confirmado_pelo_admin = (
                    request.POST.get(field_name) is not None
                )
                entry.save()

            return HttpResponseRedirect(
                reverse("tournament_entries_manage", args=[tournament.id]) + "?ok=1"
            )

        if "confirm_all_requests" in request.POST:
            entries = TournamentEntry.objects.filter(
                tournament=tournament,
                confirmou_presenca=True,
            )
            for entry in entries:
                entry.confirmado_pelo_admin = True
                entry.save()

            return HttpResponseRedirect(
                reverse("tournament_entries_manage", args=[tournament.id]) + "?ok=1"
            )

    if request.GET.get("ok"):
        mensagem = "Alterações salvas com sucesso."

    if request.GET.get("erro_status"):
        mensagem_erro = (
            "Este torneio já está em andamento ou foi finalizado. "
            "Edição de inscrições e confirmações está bloqueada."
        )

    entries = (
        TournamentEntry.objects
        .filter(tournament=tournament)
        .select_related("player")
        .order_by("-confirmou_presenca", "confirmado_pelo_admin", "player__nome")
    )

    ids_inscritos = [e.player_id for e in entries]

    players_disponiveis = (
        Player.objects
        .filter(ativo=True)
        .exclude(id__in=ids_inscritos)
        .order_by("nome")
    )

    return render(
        request,
        "tournament_entries.html",
        {
            "tournament": tournament,
            "season": season,
            "entries": entries,
            "players_disponiveis": players_disponiveis,
            "mensagem": mensagem,
            "mensagem_erro": mensagem_erro,
            "edicao_bloqueada": edicao_bloqueada,
        },
    )


# ============================================================
#  RESULTADOS DO TORNEIO (ADMIN)
# ============================================================

@admin_required
def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    season = tournament.season
    mensagem = None

    if request.method == "POST":
        entries = (
            TournamentEntry.objects
            .filter(tournament=tournament)
            .select_related("player")
        )

        for entry in entries:
            player = entry.player
            pid = player.id

            participou = request.POST.get(f"participou_{pid}") is not None
            confirmou = request.POST.get(f"confirmou_{pid}") is not None
            timechip = request.POST.get(f"timechip_{pid}") is not None

            pos_str = request.POST.get(f"pos_{pid}", "").strip()
            ajuste_str = request.POST.get(f"ajuste_{pid}", "").strip()

            entry.participou = participou
            entry.confirmou_presenca = confirmou
            entry.usou_time_chip = timechip
            entry.save()

            result = TournamentResult.objects.filter(
                tournament=tournament,
                player=player,
            ).first()

            if pos_str:
                pos = int(pos_str)
                ajuste = int(ajuste_str) if ajuste_str else 0

                if result is None:
                    result = TournamentResult(
                        tournament=tournament,
                        player=player,
                    )

                result.posicao = pos
                result.pontos_bonus = 0
                result.pontos_ajuste_deal = ajuste
                result.save()
            else:
                if result:
                    result.delete()

        tournament.recalcular_pontuacao()

        return HttpResponseRedirect(
            reverse("tournament_results", args=[tournament.id]) + "?ok=1"
        )

    if request.GET.get("ok"):
        mensagem = "Dados salvos e pontos recalculados com sucesso."

    entries = (
        TournamentEntry.objects
        .filter(tournament=tournament)
        .select_related("player")
        .order_by("player__nome")
    )

    linhas = []

    for entry in entries:
        result = TournamentResult.objects.filter(
            tournament=tournament,
            player=entry.player,
        ).first()

        linhas.append(
            {
                "player": entry.player,
                "entry": entry,
                "result": result,
            }
        )

    return render(
        request,
        "tournament_results.html",
        {
            "tournament": tournament,
            "season": season,
            "linhas": linhas,
            "mensagem": mensagem,
        },
    )
