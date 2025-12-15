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
    CALCULO_CHOICES = (
        ('FIXO', 'Pontuação Fixa'),
        ('DINAMICO', 'Dinâmico (Field + Buy-in + Posição)'),
    )
    
    nome = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)
    
    # Novo: configuração de cálculo
    tipo_calculo = models.CharField(
        max_length=20,
        choices=CALCULO_CHOICES,
        default='FIXO',
        help_text="Sistema de cálculo de pontos para ranking"
    )
    
    # Tabela de pontos fixos
    pts_1lugar = models.IntegerField(default=14, help_text="Pontos para 1º lugar")
    pts_2lugar = models.IntegerField(default=11, help_text="Pontos para 2º lugar")
    pts_3lugar = models.IntegerField(default=8, help_text="Pontos para 3º lugar")
    pts_4lugar = models.IntegerField(default=6, help_text="Pontos para 4º lugar")
    pts_5lugar = models.IntegerField(default=4, help_text="Pontos para 5º lugar")
    pts_6lugar = models.IntegerField(default=2, help_text="Pontos para 6º lugar")
    pts_7lugar = models.IntegerField(default=1, help_text="Pontos para 7º lugar")
    pts_8lugar = models.IntegerField(default=1, help_text="Pontos para 8º lugar")
    pts_9lugar = models.IntegerField(default=1, help_text="Pontos para 9º lugar")
    pts_10lugar = models.IntegerField(default=1, help_text="Pontos para 10º lugar")

    class Meta:
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"

    def __str__(self):
        return self.nome
    
    def get_tabela_pontos_fixos(self):
        """Retorna dicionário com tabela de pontos fixos"""
        return {
            1: self.pts_1lugar,
            2: self.pts_2lugar,
            3: self.pts_3lugar,
            4: self.pts_4lugar,
            5: self.pts_5lugar,
            6: self.pts_6lugar,
            7: self.pts_7lugar,
            8: self.pts_8lugar,
            9: self.pts_9lugar,
            10: self.pts_10lugar,
        }


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
#  PRODUTOS DO TORNEIO (Jack Pot, etc)
# ============================================================

class TournamentProduct(models.Model):
    """
    Produtos adicionais que os jogadores podem comprar.
    Ex: Jack Pot, Bounty, Mystery Bounce, etc.
    Não entram no pote principal.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome} (R${self.valor})"


class TournamentPrize(models.Model):
    """
    Prêmios extras (vouchers, créditos, etc) concedidos aos ganhadores.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome} (R${self.valor})"


# ============================================================
#  TORNEIOS
# ============================================================

class Tournament(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('ENCERRADO', 'Encerrado'),
        ('CANCELADO', 'Cancelado'),
    )

    RAKE_TYPE_CHOICES = (
        ('FIXO', 'Valor Fixo'),
        ('PERCENTUAL', 'Percentual'),
        ('MISTO', 'Fixo + Percentual'),
    )

    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TournamentType, on_delete=models.SET_NULL, null=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    
    data = models.DateTimeField()
    
    buyin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    permite_rebuy = models.BooleanField(default=False)
    permite_addon = models.BooleanField(default=False)
    rebuy_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    addon_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    
    # Rake Configuration
    rake_type = models.CharField(
        max_length=20,
        choices=RAKE_TYPE_CHOICES,
        default='FIXO',
        help_text="Tipo de cálculo de rake"
    )
    rake_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Rake fixo por buyin")
    rake_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Rake em % do pote")
    
    rebuy_rake_type = models.CharField(max_length=20, choices=RAKE_TYPE_CHOICES, default='FIXO', blank=True, null=True)
    rebuy_rake_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    rebuy_rake_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    
    addon_rake_type = models.CharField(max_length=20, choices=RAKE_TYPE_CHOICES, default='FIXO', blank=True, null=True)
    addon_rake_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    addon_rake_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    
    permite_rebuy_duplo = models.BooleanField(default=False)
    max_rebuys = models.IntegerField(default=0, blank=True, null=True)
    
    # Estrutura de blinds
    blind_structure = models.ForeignKey(BlindStructure, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Produtos opcionais
    produtos = models.ManyToManyField(TournamentProduct, blank=True, related_name='tournaments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    
    # Gestão
    total_jogadores = models.IntegerField(default=0, help_text="Total de jogadores que entraram")
    timechip_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text="Valor da venda de timechips (100% para house)")
    
    class Meta:
        ordering = ['-data']
        verbose_name = "Torneio"
        verbose_name_plural = "Torneios"

    def __str__(self):
        return f"{self.nome} ({self.data.strftime('%d/%m/%Y')})"

    def calcular_rake(self, tipo='buyin', valor=None):
        """
        Calcula rake baseado no tipo e configuração.
        tipo: 'buyin', 'rebuy', 'addon'
        valor: valor total (opcional)
        """
        if tipo == 'buyin':
            rake_type = self.rake_type
            rake_valor = self.rake_valor
            rake_percentual = self.rake_percentual
        elif tipo == 'rebuy':
            rake_type = self.rebuy_rake_type or self.rake_type
            rake_valor = self.rebuy_rake_valor or self.rake_valor
            rake_percentual = self.rebuy_rake_percentual or self.rake_percentual
        elif tipo == 'addon':
            rake_type = self.addon_rake_type or self.rake_type
            rake_valor = self.addon_rake_valor or self.rake_valor
            rake_percentual = self.addon_rake_percentual or self.rake_percentual
        else:
            return Decimal("0")

        if rake_type == 'FIXO':
            return Decimal(rake_valor)
        elif rake_type == 'PERCENTUAL':
            if valor:
                return Decimal(valor) * Decimal(rake_percentual) / Decimal("100")
            return Decimal("0")
        elif rake_type == 'MISTO':
            resultado = Decimal(rake_valor)
            if valor:
                resultado += Decimal(valor) * Decimal(rake_percentual) / Decimal("100")
            return resultado
        return Decimal("0")


# ============================================================
#  INSCRIÇÕES E RESULTADOS
# ============================================================

class TournamentEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    confirmou_presenca = models.BooleanField(default=False)
    confirmado_pelo_admin = models.BooleanField(default=False)
    
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    pontos_participacao = models.IntegerField(default=0, help_text="Pontos por simplesmente participar")
    
    class Meta:
        unique_together = ("tournament", "player")
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.player} - {self.tournament}"


class PlayerProductPurchase(models.Model):
    """
    Rastreia compras de produtos adicionais por jogador em um torneio.
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    product = models.ForeignKey(TournamentProduct, on_delete=models.CASCADE)
    
    quantidade = models.IntegerField(default=1)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ("tournament", "player", "product")

    def __str__(self):
        return f"{self.player} - {self.product} ({self.tournament})"


class TournamentResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    posicao = models.IntegerField(blank=True, null=True)
    pontos_base = models.IntegerField(default=0)
    pontos_bonus = models.IntegerField(default=0)
    pontos_ajuste_deal = models.IntegerField(default=0)
    pontos_finais = models.IntegerField(default=0)
    
    premiacao_recebida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Prêmios extras concedidos
    premio_extra = models.OneToOneField(
        TournamentPrize, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resultado'
    )

    class Meta:
        unique_together = ("tournament", "player")
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"

    def __str__(self):
        return f"{self.tournament} - {self.player} ({self.pontos_finais} pts)"

    def calcular_pontos(self):
        """
        Calcula pontos_finais baseado na configuração da temporada.
        Considera pontos_base, pontos_bonus e ajustes.
        """
        from .views.season import calcular_pontos_posicao
        
        season = self.tournament.season
        
        if season.tipo_calculo == 'FIXO':
            # Sistema fixo
            tabela = season.get_tabela_pontos_fixos()
            pts = calcular_pontos_posicao(
                self.posicao, 
                self.tournament.total_jogadores,
                self.tournament.buyin,
                self.tournament.tipo.multiplicador_pontos if self.tournament.tipo else Decimal("1.00"),
                tabela_fixa=tabela
            )
        else:
            # Sistema dinâmico
            pts = calcular_pontos_posicao(
                self.posicao,
                self.tournament.total_jogadores,
                self.tournament.buyin,
                self.tournament.tipo.multiplicador_pontos if self.tournament.tipo else Decimal("1.00")
            )
        
        # Adiciona bônus e ajustes
        self.pontos_finais = pts + self.pontos_bonus + self.pontos_ajuste_deal
        return self.pontos_finais


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


# ============================================================
#  ESTATÍSTICAS DO JOGADOR
# ============================================================

class PlayerStatistics(models.Model):
    """
    Armazena estatísticas consolidadas de um jogador em uma temporada.
    Permite cálculos rápidos no ranking sem processar todos os torneios.
    """
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    # Participações
    total_torneios = models.IntegerField(default=0)  # Total de inscrições
    torneios_com_resultado = models.IntegerField(default=0)  # Com posição registrada
    
    # Prêmios
    vitórias = models.IntegerField(default=0)  # 1º lugares
    top_3 = models.IntegerField(default=0)  # Finalizações top 3
    top_5 = models.IntegerField(default=0)  # Finalizações top 5
    
    # Financeiro
    total_buyin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_premio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    roi = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # (Prêmios - Buy-ins) / Buy-ins * 100
    
    # Taxa de ITM (In The Money)
    taxa_itm = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # % de prêmios
    
    # Pontos
    pontos_totais = models.IntegerField(default=0)
    media_pontos = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Última atualização
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("season", "player")
        verbose_name = "Estatística do Jogador"
        verbose_name_plural = "Estatísticas do Jogador"
    
    def __str__(self):
        return f"{self.player} - {self.season} ({self.pontos_totais} pts)"


class PlayerAchievement(models.Model):
    """
    Badges/achievements conquistados pelos jogadores.
    """
    ACHIEVEMENT_TYPES = (
        ('CAMPEAO', 'Campeão'),
        ('FINALISTA', 'Finalista'),
        ('CONSISTENTE', 'Consistente'),
        ('CRAQUE', 'Craque'),
        ('STREAKER', 'Streaker'),
        ('ALL_IN', 'All-in'),
        ('COMEBACK', 'Comeback'),
        ('HOT_STREAK', 'Hot Streak'),
    )
    
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    descricao = models.CharField(max_length=200)
    obtido_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("season", "player", "tipo")
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
    
    def __str__(self):
        return f"{self.player} - {self.get_tipo_display()} ({self.season})"