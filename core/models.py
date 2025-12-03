from decimal import Decimal
from django.conf import settings
from django.db import models


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
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.apelido or self.nome


class Tournament(models.Model):
    STATUS_CHOICES = (
        ("AGENDADO", "Agendado"),
        ("EM_ANDAMENTO", "Em andamento"),
        ("FINALIZADO", "Finalizado"),
    )

    nome = models.CharField(max_length=150)
    data = models.DateTimeField()
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TournamentType, on_delete=models.PROTECT)

    buy_in = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    garantido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AGENDADO",
    )

    def __str__(self):
        return f"{self.nome} ({self.data:%d/%m/%Y})"

    # ---------- REGRA DE PONTUAÇÃO ----------
    def _pontos_posicao_base(self, posicao: int) -> int:
        """
        Tabela padrão da imagem:
        1º 14 | 2º 11 | 3º 9 | 4º 7 | 5º 6 | 6º 5 | 7º 4 | 8º 3 | 9º 2
        """
        mapa = {
            1: 14,
            2: 11,
            3: 9,
            4: 7,
            5: 6,
            6: 5,
            7: 4,
            8: 3,
            9: 2,
        }
        return mapa.get(posicao, 0)

    def recalcular_pontuacao(self):
        """
        Recalcula todos os TournamentResult deste torneio
        aplicando:
        - pontos pela posição (tabela padrão * multiplicador)
        - +1 participação
        - +1 time chip
        - +1 confirmação
        - +ajuste deal
        E grava em `pontos_finais`.
        """
        multiplicador = self.tipo.multiplicador_pontos or Decimal("1.00")

        entries = TournamentEntry.objects.filter(tournament=self).select_related(
            "player"
        )

        for entry in entries:
            result, _ = TournamentResult.objects.get_or_create(
                tournament=self,
                player=entry.player,
                defaults={
                    "posicao": None,
                    "pontos_base": 0,
                    "pontos_bonus": 0,
                    "pontos_ajuste_deal": 0,
                    "pontos_finais": 0,
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
            result.pontos_finais = (
                base + bonus + (result.pontos_ajuste_deal or 0)
            )
            result.save()

            # guarda na entry o total de pontos de participação
            entry.pontos_participacao = bonus
            entry.save()


class TournamentEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    participou = models.BooleanField(default=False)
    confirmou_presenca = models.BooleanField(default=False)
    # ✅ novo campo: confirmação oficial do organizador
    confirmado_pelo_admin = models.BooleanField(
        default=False,
        help_text="Presença confirmada pelo organizador.",
    )
    usou_time_chip = models.BooleanField(default=False)

    pontos_participacao = models.IntegerField(default=0)

    class Meta:
        unique_together = ("tournament", "player")

    def __str__(self):
        return f"{self.tournament} - {self.player}"


class TournamentResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    posicao = models.IntegerField(blank=True, null=True)
    pontos_base = models.IntegerField(default=0)
    pontos_bonus = models.IntegerField(default=0)
    pontos_ajuste_deal = models.IntegerField(default=0)
    pontos_finais = models.IntegerField(default=0)

    class Meta:
        unique_together = ("tournament", "player")

    def __str__(self):
        return f"{self.tournament} - {self.player} ({self.pontos_finais} pts)"


# ---------- Pontos iniciais por temporada ----------
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
