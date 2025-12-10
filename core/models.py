from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

# ============================================================
#  ESTRUTURA DE BLINDS
# ============================================================

class BlindStructure(models.Model):
    """
    Define um template de estrutura (ex: 'Turbo 15min', 'Deepstack 30min').
    """
    nome = models.CharField(max_length=100, help_text="Ex: Regular 20min")
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class BlindLevel(models.Model):
    """
    Cada nível da estrutura (Level 1, Level 2, Break, etc).
    """
    structure = models.ForeignKey(BlindStructure, on_delete=models.CASCADE, related_name='levels')
    ordem = models.PositiveIntegerField(help_text="1 para o primeiro nível, 2 para o segundo...")
    
    small_blind = models.IntegerField(default=0)
    big_blind = models.IntegerField(default=0)
    ante = models.IntegerField(default=0, help_text="Ante único (Big Blind Ante) ou total da mesa")
    
    tempo_minutos = models.PositiveIntegerField(default=20)
    is_break = models.BooleanField(default=False, verbose_name="É intervalo?")
    
    class Meta:
        ordering = ['ordem']
        unique_together = ('structure', 'ordem')

    def __str__(self):
        if self.is_break:
            return f"{self.ordem} - Intervalo ({self.tempo_minutos}m)"
        return f"{self.ordem} - {self.small_blind}/{self.big_blind} ({self.tempo_minutos}m)"


# ============================================================
#  MODELOS BÁSICOS (Season, Type, Player)
# ============================================================

class Season(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class TournamentType(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    buyin_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rake_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor retido pela casa")

    multiplicador_pontos = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
    )
    usa_regras_padrao = models.BooleanField(
        default=True,
        help_text="Se marcado, usa a tabela padrão (1º=14, 2º=11, ..., 9º=2)",
    )

    def __str__(self):
        return f"{self.nome} (peso {self.multiplicador_pontos})"


class Player(models.Model):
    STATUS_CHOICES = (
        ('ATIVO', 'Ativo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('VIP', 'VIP'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_profile",
        help_text="Usuário do sistema vinculado a este jogador (login do site).",
    )

    nome = models.CharField(max_length=150)
    apelido = models.CharField(max_length=80, blank=True, null=True)
    cpf = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    
    email = models.EmailField(max_length=254, blank=True, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO')
    observacoes = models.TextField(blank=True, null=True, help_text="Notas internas sobre o jogador")
    
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.apelido or self.nome


# ============================================================
#  TORNEIO (Completo)
# ============================================================

class Tournament(models.Model):
    STATUS_CHOICES = (
        ("AGENDADO", "Agendado"),
        ("EM_ANDAMENTO", "Em andamento"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    )

    nome = models.CharField(max_length=150)
    data = models.DateTimeField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TournamentType, on_delete=models.PROTECT)

    # Financeiro do Torneio
    buy_in = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rake = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Taxa administrativa")
    garantido = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stack_inicial = models.IntegerField(default=10000, help_text="Fichas iniciais")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AGENDADO",
    )

    # Controle de Estrutura e Relógio
    blind_structure = models.ForeignKey(
        BlindStructure, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Estrutura de blinds usada neste torneio"
    )
    current_level_order = models.IntegerField(default=1, help_text="Qual nível de blind está rodando agora?")
    is_paused = models.BooleanField(default=False, help_text="O relógio está pausado?")
    
    # Campos novos para o Timer (Turno 10)
    last_level_start = models.DateTimeField(null=True, blank=True, help_text="Hora que o nível começou ou despausou")
    seconds_remaining_at_pause = models.IntegerField(null=True, blank=True, help_text="Segundos restantes quando pausou")

    # Controle de Mesa (Seat Draw)
    max_players_per_table = models.IntegerField(default=9, help_text="Max de jogadores por mesa (9-max, 6-max)")
    active_tables = models.IntegerField(default=0, help_text="Número de mesas ativas no momento")

    def __str__(self):
        return f"{self.nome} ({self.data:%d/%m/%Y})"

    def get_current_blind(self):
        if not self.blind_structure:
            return None
        return self.blind_structure.levels.filter(ordem=self.current_level_order).first()

    # ---------- REGRA DE PONTUAÇÃO ----------
    def _pontos_posicao_base(self, posicao: int) -> int:
        mapa = {
            1: 14, 2: 11, 3: 9, 4: 7, 5: 6, 
            6: 5, 7: 4, 8: 3, 9: 2,
        }
        return mapa.get(posicao, 0)

    def recalcular_pontuacao(self):
        multiplicador = self.tipo.multiplicador_pontos or Decimal("1.00")
        entries = TournamentEntry.objects.filter(tournament=self).select_related("player")

        for entry in entries:
            result, _ = TournamentResult.objects.get_or_create(
                tournament=self,
                player=entry.player,
                defaults={
                    "posicao": None, "pontos_base": 0, "pontos_bonus": 0,
                    "pontos_ajuste_deal": 0, "pontos_finais": 0,
                },
            )

            if result.posicao:
                base = self._pontos_posicao_base(result.posicao)
            else:
                base = 0

            base = int(base * multiplicador)
            
            pontos_participacao = 1 if entry.participou else 0
            pontos_time_chip = 1 if entry.usou_time_chip else 0
            pontos_confirmacao = 1 if entry.confirmou_presenca else 0

            bonus = pontos_participacao + pontos_time_chip + pontos_confirmacao

            result.pontos_base = base
            result.pontos_bonus = bonus
            result.pontos_finais = base + bonus + (result.pontos_ajuste_deal or 0)
            result.save()

            entry.pontos_participacao = bonus
            entry.save()


# ============================================================
#  INSCRIÇÃO (Gestão de Mesa e Financeiro do Jogador)
# ============================================================

class TournamentEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='entries')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # Status e Presença
    participou = models.BooleanField(default=False)
    confirmou_presenca = models.BooleanField(default=False)
    confirmado_pelo_admin = models.BooleanField(default=False)
    usou_time_chip = models.BooleanField(default=False)

    # Controle de Jogo (Eliminação e Seat Draw)
    ativo_no_jogo = models.BooleanField(default=True, help_text="False se o jogador já caiu")
    eliminado_em = models.DateTimeField(null=True, blank=True)
    posicao_eliminacao = models.IntegerField(null=True, blank=True)
    
    mesa = models.IntegerField(null=True, blank=True, help_text="Número da mesa")
    cadeira = models.IntegerField(null=True, blank=True, help_text="Número da cadeira")

    # Financeiro do Jogador no Torneio
    buyin_pago = models.BooleanField(default=False)
    qtde_rebuys = models.IntegerField(default=0)
    qtde_addons = models.IntegerField(default=0)
    valor_total_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    pontos_participacao = models.IntegerField(default=0)

    class Meta:
        unique_together = ("tournament", "player")

    def __str__(self):
        status = "JOGANDO" if self.ativo_no_jogo else f"OUT ({self.posicao_eliminacao}º)"
        local = f"M{self.mesa}-C{self.cadeira}" if self.mesa else "Sem lugar"
        return f"{self.player.apelido} - {local} [{status}]"


# ============================================================
#  RESULTADO FINAL
# ============================================================

class TournamentResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    posicao = models.IntegerField(blank=True, null=True)
    pontos_base = models.IntegerField(default=0)
    pontos_bonus = models.IntegerField(default=0)
    pontos_ajuste_deal = models.IntegerField(default=0)
    pontos_finais = models.IntegerField(default=0)
    
    premiacao_recebida = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("tournament", "player")

    def __str__(self):
        return f"{self.tournament} - {self.player} ({self.pontos_finais} pts)"


# ============================================================
#  PONTOS INICIAIS
# ============================================================

class SeasonInitialPoints(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pontos_iniciais = models.IntegerField(default=0)

    class Meta:
        unique_together = ("season", "player")
        verbose_name = "Pontos iniciais da temporada"
        verbose_name_plural = "Pontos iniciais da temporada"

    def __str__(self):
        return f"{self.season} - {self.player} ({self.pontos_iniciais} pts iniciais)"