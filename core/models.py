from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ============================================================
#  MODELOS DE MULTI-TENANT
# ============================================================

class Tenant(models.Model):
    """
    Representa uma organização/grupo independente no sistema.
    """
    # INFORMAÇÕES BÁSICAS
    nome = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='tenant_logos/%Y/%m/',
        blank=True,
        null=True,
        help_text="Logo do clube para exibir nas telas (recomendado: 200x200px)"
    )
    
    # INFORMAÇÕES DE CONTATO DO CLUBE
    club_email = models.EmailField(blank=True, help_text="Email de contato do clube")
    club_phone = models.CharField(max_length=20, blank=True, help_text="Telefone principal")
    club_cnpj = models.CharField(
        max_length=18, 
        blank=True, 
        unique=True, 
        null=True,
        help_text="Formato: XX.XXX.XXX/XXXX-XX"
    )
    club_website = models.URLField(blank=True, help_text="Website do clube")
    
    # ENDEREÇO
    address_cep = models.CharField(max_length=9, blank=True, help_text="Formato: XXXXX-XXX")
    address_street = models.CharField(max_length=255, blank=True, help_text="Nome da rua/avenida")
    address_number = models.CharField(max_length=20, blank=True, help_text="Número do imóvel")
    address_complement = models.CharField(max_length=100, blank=True, help_text="Apto, sala, etc")
    address_neighborhood = models.CharField(max_length=100, blank=True, help_text="Bairro")
    address_city = models.CharField(max_length=100, blank=True, help_text="Cidade")
    address_state = models.CharField(
        max_length=2, 
        blank=True,
        help_text="UF (SP, RJ, MG, etc)"
    )
    
    # INFORMAÇÕES DO ADMINISTRADOR
    admin_full_name = models.CharField(max_length=255, blank=True, help_text="Nome completo do contato")
    admin_phone = models.CharField(max_length=20, blank=True, help_text="Telefone do administrador")
    admin_cpf = models.CharField(
        max_length=14, 
        blank=True,
        help_text="Formato: XXX.XXX.XXX-XX (opcional)"
    )
    admin_role = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Cargo/Função (Proprietário, Gerente, etc)"
    )
    
    # LIMITES OPCIONAIS
    max_jogadores = models.IntegerField(null=True, blank=True)
    max_torneios = models.IntegerField(null=True, blank=True)
    
    # METADADOS
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class TenantUser(models.Model):
    """
    Relaciona usuários a tenants e define papéis.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('moderator', 'Moderador'),
        ('player', 'Jogador'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_users')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
    adicionado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'tenant']
        ordering = ['-adicionado_em']
    
    def __str__(self):
        return f"{self.user.username} - {self.tenant.nome} ({self.role})"

# ============================================================
#  ESTRUTURA DE BLINDS
# ============================================================

class BlindStructure(models.Model):
    """
    Define um template de estrutura (ex: 'Turbo 15min', 'Deepstack 30min').
    """
    nome = models.CharField(max_length=100, help_text="Ex: Regular 20min")
    descricao = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome
    
    def has_levels(self):
        """Verifica se a estrutura tem níveis de blind definidos"""
        return self.levels.exists()
    
    def get_levels_count(self):
        """Retorna a quantidade de níveis definidos"""
        return self.levels.count()
    
    def get_total_duration_minutes(self):
        """Retorna a duração total em minutos"""
        return sum(level.tempo_minutos for level in self.levels.all())


class BlindLevel(models.Model):
    """
    Cada nível da estrutura (Level 1, Level 2, Break, etc).
    """
    structure = models.ForeignKey(BlindStructure, on_delete=models.CASCADE, related_name='levels')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    buyin_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rake_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor retido pela casa")

    # Multiplicador de pontos - apenas usado no modo FIXO
    multiplicador_pontos = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text="Multiplicador de pontos (apenas usado no modo de pontuação FIXO)"
    )
    usa_regras_padrao = models.BooleanField(
        default=True,
        help_text="Se marcado, usa a tabela padrão (1º=14, 2º=11, ..., 9º=2)",
    )

    def __str__(self):
        return self.nome


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
    foto = models.ImageField(upload_to='player_photos/%Y/%m/', blank=True, null=True, help_text="Foto do jogador")
    
    email = models.EmailField(max_length=254, blank=True, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO')
    observacoes = models.TextField(blank=True, null=True, help_text="Notas internas sobre o jogador")
    
    ativo = models.BooleanField(default=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.apelido or self.nome


# ============================================================
#  PRODUTOS DO TORNEIO (Jack Pot, etc)
# ============================================================

class TournamentProduct(models.Model):
    """
    Produtos adicionais que os jogadores podem comprar.
    Ex: Jack Pot, Bounty, Mystery Bounce, Time Chip, etc.
    Alguns entram no pote (Add-on, Rebuy), outros não (Jack Pot, Staff).
    Alguns adicionam fichas ao jogo (Time Chip, Jack Pot), outros não (Staff, Bounty).
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    entra_em_premiacao = models.BooleanField(
        default=False,
        help_text="Marque se este produto entra para o cálculo de premiação (ex: Add-on, Rebuy entram; Jack Pot, Staff não entram)"
    )
    chips_amount = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Quantidade de fichas que este produto adiciona ao jogo (0 ou vazio = não adiciona)"
    )
    quantidade_maxima = models.IntegerField(
        default=0,
        blank=True,
        help_text="Máximo de vezes que este produto pode ser comprado (0 = ilimitado)"
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} (R${self.valor})"


class TournamentPrize(models.Model):
    """
    Prêmios extras (vouchers, créditos, etc) concedidos aos ganhadores.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    data = models.DateTimeField()
    
    buyin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buyin_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas do buy-in inicial")
    
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
    
    # Rebuy & Add-on Configuration
    permite_rebuy = models.BooleanField(default=False, help_text="Permite rebuy simples")
    rebuy_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text="Valor do rebuy simples")
    rebuy_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas do rebuy simples")
    
    permite_rebuy_duplo = models.BooleanField(default=False, help_text="Permite rebuy duplo (2x ou valor diferenciado)")
    rebuy_duplo_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text="Valor do rebuy duplo (se diferente, 2x rebuy simples)")
    rebuy_duplo_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas do rebuy duplo")
    
    permite_addon = models.BooleanField(default=False, help_text="Permite add-on (máx 1x por jogador)")
    addon_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text="Valor do add-on")
    addon_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas do add-on")
    
    # STAFF (Taxa obrigatória)
    staff_valor = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, help_text="Taxa de STAFF cobrada no primeiro buy-in")
    staff_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas que o STAFF adiciona (se houver)")
    staff_obrigatorio = models.BooleanField(default=False, help_text="Se marcado, STAFF é obrigatório no primeiro buy-in")
    
    # TIME CHIP (Fichas extras quando jogador chega a tempo - sem valor de compra)
    timechip_chips = models.IntegerField(default=0, null=True, blank=True, help_text="Quantidade de fichas do Time Chip (confirmado pelo diretor)")
    
    # Estrutura de blinds
    blind_structure = models.ForeignKey(BlindStructure, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Produtos opcionais
    produtos = models.ManyToManyField(TournamentProduct, blank=True, related_name='tournaments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    
    # Gestão
    total_jogadores = models.IntegerField(default=0, help_text="Total de jogadores que entraram")
    
    # Controle de Timer do Diretor
    is_paused = models.BooleanField(default=True, help_text="Se o timer está pausado")
    last_level_start = models.DateTimeField(null=True, blank=True, help_text="Quando o nível atual começou")
    seconds_remaining_at_pause = models.IntegerField(null=True, blank=True, help_text="Segundos restantes quando pausado")
    current_level_order = models.IntegerField(default=1, help_text="Ordem do nível atual de blinds")
    
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
    
    def get_prize_pool(self):
        """
        Calcula o pote total de prêmios (tudo que foi coletado menos o rake total).
        Inclui buy-in, rebuys, add-ons e staff.
        """
        total_coletado = Decimal("0")
        
        # Buy-in base
        entries_count = TournamentEntry.objects.filter(tournament=self).count()
        total_coletado += Decimal(self.buyin) * entries_count
        
        # Rebuys - buscar em TournamentPlayerPurchase
        rebuy_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='REBUY'
        )
        for purchase in rebuy_purchases:
            total_coletado += Decimal(purchase.valor) * purchase.quantidade
        
        # Rebuy Duplo
        rebuy_duplo_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='REBUY_DUPLO'
        )
        for purchase in rebuy_duplo_purchases:
            total_coletado += Decimal(purchase.valor) * purchase.quantidade
        
        # Add-on
        addon_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='ADDON'
        )
        for purchase in addon_purchases:
            total_coletado += Decimal(purchase.valor) * purchase.quantidade
        
        # Descontar rake total
        rake_total = Decimal("0")
        rake_total += self.calcular_rake('buyin', self.buyin) * entries_count
        
        for purchase in rebuy_purchases:
            rake_total += self.calcular_rake('rebuy', purchase.valor) * purchase.quantidade
        
        for purchase in rebuy_duplo_purchases:
            rake_total += self.calcular_rake('rebuy', purchase.valor) * purchase.quantidade
        
        for purchase in addon_purchases:
            rake_total += self.calcular_rake('addon', purchase.valor) * purchase.quantidade
        
        prize_pool = total_coletado - rake_total
        return prize_pool if prize_pool > 0 else Decimal("0")
    
    def get_recommended_itm_count(self):
        """
        Recomenda quantas pessoas devem ser premiadas baseado no número de entradas.
        Segue a regra dos 15% do field (padrão internacional).
        """
        entries_count = TournamentEntry.objects.filter(tournament=self).count()
        
        # Regra dos 15% com mínimo de 3
        recommended = max(3, int(entries_count * 0.15))
        
        # Casos especiais para poucos players
        if entries_count <= 5:
            return min(2, entries_count)
        elif entries_count <= 10:
            return 3
        elif entries_count <= 20:
            return 3 if entries_count < 18 else 4
        elif entries_count <= 30:
            return 4 if entries_count < 25 else 5
        else:
            return recommended
    
    def get_current_blind(self):
        """
        Retorna o nível de blind atual baseado no tempo decorrido desde o início.
        Retorna None se não tem estrutura de blinds definida.
        """
        if not self.blind_structure:
            return None
        
        from django.utils import timezone
        
        # Se o torneio ainda não começou
        if not self.last_level_start:
            return self.blind_structure.levels.filter(ordem=1).first()
        
        # Calcular quanto tempo passou desde o início
        now = timezone.now()
        
        # Se está pausado, calcular com base no tempo restante
        if self.is_paused and self.seconds_remaining_at_pause is not None:
            # Retornar o nível atual armazenado
            return self.blind_structure.levels.filter(ordem=self.current_level_order).first()
        
        # Calcular tempo total decorrido
        elapsed_seconds = int((now - self.last_level_start).total_seconds())
        
        # Acumular tempos de nível para encontrar o nível atual
        total_time = 0
        levels = self.blind_structure.levels.all().order_by('ordem')
        
        for level in levels:
            level_duration = level.tempo_minutos * 60
            if total_time + level_duration > elapsed_seconds:
                return level
            total_time += level_duration
        
        # Se passou de todos os níveis, retornar o último
        return levels.last()
    
    def get_active_players_count(self):
        """Retorna quantidade de jogadores inscritos (participantes)"""
        return self.tournamententry_set.count()
    
    def get_average_stack(self):
        """Calcula o stack médio dos jogadores (em FICHAS, não em dinheiro)"""
        entries_count = self.get_active_players_count()
        if entries_count == 0:
            return 0
        
        # Calcular total de fichas distribuídas
        total_chips = 0
        
        # Fichas do buy-in
        if self.buyin_chips:
            total_chips += self.buyin_chips * entries_count
        
        # Rebuys simples
        rebuy_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='REBUY'
        )
        for purchase in rebuy_purchases:
            if self.rebuy_chips:
                total_chips += self.rebuy_chips * purchase.quantidade
        
        # Rebuys duplos
        rebuy_duplo_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='REBUY_DUPLO'
        )
        for purchase in rebuy_duplo_purchases:
            if self.rebuy_duplo_chips:
                total_chips += self.rebuy_duplo_chips * purchase.quantidade
        
        # Add-ons
        addon_purchases = TournamentPlayerPurchase.objects.filter(
            tournament=self,
            tipo='ADDON'
        )
        for purchase in addon_purchases:
            if self.addon_chips:
                total_chips += self.addon_chips * purchase.quantidade
        
        # STAFF (se adiciona fichas)
        if self.staff_chips:
            staff_purchases = TournamentEntry.objects.filter(
                tournament=self,
                confirmado_pelo_admin=True
            ).count()
            total_chips += self.staff_chips * staff_purchases
        
        # TIME CHIP (director confirmation com fichas)
        if self.timechip_chips:
            timechip_purchases = TournamentPlayerPurchase.objects.filter(
                tournament=self,
                tipo='TIME_CHIP'
            ).count()
            total_chips += self.timechip_chips * timechip_purchases
        
        # Produtos com fichas (Jack Pot, etc)
        products_with_chips = TournamentProduct.objects.filter(
            chips_amount__gt=0
        ).values_list('id', 'chips_amount')
        
        for product_id, chips_amount in products_with_chips:
            product_purchases = PlayerProductPurchase.objects.filter(
                tournament=self,
                product_id=product_id
            ).aggregate(total=models.Sum('quantidade'))['total'] or 0
            total_chips += chips_amount * product_purchases
        
        if total_chips == 0:
            return 0
        
        # Stack médio = total de fichas / número de jogadores
        return int(total_chips / entries_count)
    
    def get_active_tables_count(self):
        """Calcula quantidade estimada de mesas (9 players por mesa)"""
        players = self.get_active_players_count()
        if players == 0:
            return 0
        # 9 jogadores por mesa
        tables = (players + 8) // 9  # Arredonda para cima
        return max(1, tables)
    
    def delete(self, *args, **kwargs):
        """
        Impede deleção de torneios que possuem resultados, entradas ou compras de fichas.
        """
        from django.core.exceptions import ProtectedError
        
        # Verificar se existem resultados
        if TournamentResult.objects.filter(tournament=self).exists():
            raise ProtectedError(
                f"Não é possível excluir o torneio '{self.nome}' porque já existem resultados lançados.",
                self
            )
        
        # Verificar se existem entradas (inscrições)
        if TournamentEntry.objects.filter(tournament=self).exists():
            raise ProtectedError(
                f"Não é possível excluir o torneio '{self.nome}' porque já existem inscrições de jogadores.",
                self
            )
        
        # Verificar se existem compras de fichas (rebuys, add-ons)
        if TournamentPlayerPurchase.objects.filter(tournament=self).exists():
            raise ProtectedError(
                f"Não é possível excluir o torneio '{self.nome}' porque já existem compras de rebuys/add-ons registradas.",
                self
            )
        
        # Verificar se existem prêmios lançados
        if TournamentPrize.objects.filter(tournament=self).exists():
            raise ProtectedError(
                f"Não é possível excluir o torneio '{self.nome}' porque já existem prêmios configurados.",
                self
            )
        
        # Se passou por todas as verificações, permite a exclusão
        return super().delete(*args, **kwargs)


# ============================================================
#  INSCRIÇÕES E RESULTADOS
# ============================================================

class TournamentEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    confirmou_presenca = models.BooleanField(default=False)
    confirmado_pelo_admin = models.BooleanField(default=False)
    
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    pontos_participacao = models.IntegerField(default=0, help_text="Pontos por simplesmente participar")
    
    class Meta:
        unique_together = ("tournament", "player", "tenant")
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.player} - {self.tournament}"
    
    def get_rebuy_count(self):
        """Retorna quantidade de rebuys simples"""
        purchase = PlayerProductPurchase.objects.filter(
            tournament=self.tournament,
            player=self.player,
            product__nome='REBUY'
        ).first()
        return purchase.quantidade if purchase else 0
    
    def get_rebuy_duplo_count(self):
        """Retorna quantidade de rebuys duplos"""
        purchase = PlayerProductPurchase.objects.filter(
            tournament=self.tournament,
            player=self.player,
            product__nome='REBUY_DUPLO'
        ).first()
        return purchase.quantidade if purchase else 0
    
    def get_addon_count(self):
        """Retorna quantidade de add-ons (máximo 1)"""
        purchase = PlayerProductPurchase.objects.filter(
            tournament=self.tournament,
            player=self.player,
            product__nome='ADDON'
        ).first()
        return purchase.quantidade if purchase else 0
    
    def get_timechip_count(self):
        """Retorna se jogador tem time chip confirmado (máximo 1)"""
        purchase = PlayerProductPurchase.objects.filter(
            tournament=self.tournament,
            player=self.player,
            product__nome='TIME_CHIP'
        ).first()
        return purchase.quantidade if purchase else 0


class TournamentPlayerPurchase(models.Model):
    """
    Rastreia compras de produtos adicionais (Rebuy, Add-on, Time Chip) por jogador.
    Permite múltiplos rebuys (quantidade > 1), mas add-on limitado a 1.
    Time Chip é confirmado pelo diretor (não é compra monetária).
    """
    TIPO_CHOICES = (
        ('REBUY', 'Rebuy'),
        ('REBUY_DUPLO', 'Rebuy Duplo'),
        ('ADDON', 'Add-on'),
        ('TIME_CHIP', 'Time Chip'),
    )
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.IntegerField(default=1)
    data_compra = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Compra de Jogador"
        verbose_name_plural = "Compras de Jogador"
        unique_together = ('tournament', 'player', 'tipo')
    
    def __str__(self):
        return f"{self.player} - {self.get_tipo_display()} x{self.quantidade} (R${self.valor})"
    
    @property
    def valor_total(self):
        """Valor total da compra (valor do produto * quantidade)"""
        return self.valor * self.quantidade


class PlayerProductPurchase(models.Model):
    """
    Rastreia compras de produtos adicionais por jogador em um torneio.
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    product = models.ForeignKey(TournamentProduct, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    quantidade = models.IntegerField(default=1)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ("tournament", "player", "product")

    def __str__(self):
        return f"{self.player} - {self.product} ({self.tournament})"


class TournamentResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

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
        - FIXO: Usa tabela pré-definida + multiplicador do tipo de torneio
        - DINÂMICO: Usa cálculo automático baseado em buy-in e número de participantes
        """
        from .views.season import calcular_pontos_posicao
        
        season = self.tournament.season
        
        if season.tipo_calculo == 'FIXO':
            # Sistema fixo: tabela pré-definida + multiplicador
            tabela = season.get_tabela_pontos_fixos()
            pts = calcular_pontos_posicao(
                self.posicao, 
                self.tournament.total_jogadores,
                self.tournament.buyin,
                multiplicador_tipo=self.tournament.tipo.multiplicador_pontos,
                tabela_fixa=tabela
            )
        else:
            # Sistema dinâmico: automático baseado em buy-in e participantes
            pts = calcular_pontos_posicao(
                self.posicao,
                self.tournament.total_jogadores,
                self.tournament.buyin
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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    pontos_iniciais = models.IntegerField(default=0)

    class Meta:
        unique_together = ("season", "player", "tenant")
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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
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
        unique_together = ("season", "player", "tenant")
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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    descricao = models.CharField(max_length=200)
    obtido_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("season", "player", "tipo")
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
    
    def __str__(self):
        return f"{self.player} - {self.get_tipo_display()} ({self.season})"


# ============================================================
#  AUDITORIA FINANCEIRA
# ============================================================

class FinancialReconciliation(models.Model):
    """
    Modelo para rastrear reconciliação financeira de torneios.
    Detecta discrepâncias e mantém histórico.
    """
    STATUS_CHOICES = (
        ('OK', 'Reconciliado ✓'),
        ('DISCREPANCY', 'Discrepância ⚠️'),
        ('ERROR', 'Erro Crítico ❌'),
    )
    
    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name='reconciliation')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    # Valores esperados (calculados)
    faturamento_esperado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rake_esperado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premio_pool_esperado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Valores reais (recebidos)
    faturamento_real = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premios_pagos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Discrepância
    diferenca = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OK')
    
    # Nota sobre discrepância
    observacao = models.TextField(blank=True, null=True)
    
    # Controle
    reconciliado_em = models.DateTimeField(auto_now=True)
    reconciliado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-reconciliado_em']
        verbose_name = "Reconciliação Financeira"
        verbose_name_plural = "Reconciliações Financeiras"
    
    def __str__(self):
        return f"{self.tournament.nome} - {self.status}"
    
    def calcular_diferenca(self):
        """Calcula se há discrepância"""
        self.diferenca = self.faturamento_real - self.faturamento_esperado
        
        if abs(self.diferenca) < 0.01:  # Diferença insignificante (centavos)
            self.status = 'OK'
        elif abs(self.diferenca) > 100:  # Diferença significativa
            self.status = 'ERROR'
        else:
            self.status = 'DISCREPANCY'
        
        return self.diferenca


class FinancialLog(models.Model):
    """
    Auditoria de todas as transações financeiras.
    Quem/quando fez cada alteração.
    """
    TIPO_CHOICES = (
        ('ENTRY', 'Entrada de Buy-in'),
        ('REBUY', 'Rebuy'),
        ('ADDON', 'Add-on'),
        ('PRIZE', 'Premiação'),
        ('RAKE', 'Rake/Taxa'),
        ('REFUND', 'Devolução'),
        ('ADJUSTMENT', 'Ajuste'),
    )
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='financial_logs')
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.CharField(max_length=255)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_logs_created')
    
    # Para rastrear correções
    alterado_em = models.DateTimeField(null=True, blank=True)
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_logs_edited')
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Log Financeiro"
        verbose_name_plural = "Logs Financeiros"
        indexes = [
            models.Index(fields=['tournament', 'criado_em']),
            models.Index(fields=['player', 'criado_em']),
        ]
    
    def __str__(self):
        return f"{self.tournament} - {self.get_tipo_display()} - R${self.valor}"


# ============================================================
#  SISTEMA DE DIVISÃO DE PREMIAÇÃO
# ============================================================

class PrizeStructure(models.Model):
    """
    Define a estrutura de premiação para um torneio.
    Suporta dois modos: PERCENTUAL (% do pote) e FIXO (valores em R$)
    """
    MODO_CHOICES = [
        ('PERCENTUAL', 'Percentual do Pote'),
        ('FIXO', 'Valores Fixos (R$)'),
    ]
    
    tournament = models.OneToOneField(
        Tournament,
        on_delete=models.CASCADE,
        related_name='prize_structure',
        null=True,
        blank=True
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    
    # Modo de operação
    modo = models.CharField(max_length=20, choices=MODO_CHOICES, default='PERCENTUAL')
    
    # Informações do pote
    total_prize_pool = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Valor total disponível para distribuição"
    )
    itm_count = models.IntegerField(
        help_text="Quantidade de posições premiadas (In The Money)"
    )
    
    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prize_structures_created'
    )
    
    # Flags
    finalizado = models.BooleanField(default=False, help_text="Se True, não pode ser editado")
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Estrutura de Prêmios"
        verbose_name_plural = "Estruturas de Prêmios"
        indexes = [
            models.Index(fields=['tournament', 'criado_em']),
            models.Index(fields=['tenant', 'criado_em']),
        ]
    
    def __str__(self):
        return f"Prêmios {self.tournament} - {self.get_modo_display()}"
    
    def get_total_distributed(self):
        """Retorna o total já distribuído em prêmios"""
        return sum(
            payment.amount for payment in self.payments.all() if payment.amount
        )
    
    def get_remaining_amount(self):
        """Retorna quanto ainda precisa distribuir"""
        return self.total_prize_pool - self.get_total_distributed()


class PrizePayment(models.Model):
    """
    Registra o valor de prêmio para cada posição no torneio.
    Pode estar vinculado a um jogador específico ou apenas ser um lugar vago.
    """
    prize_structure = models.ForeignKey(
        PrizeStructure,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # Posição no ranking
    position = models.IntegerField(help_text="1º, 2º, 3º lugar, etc")
    
    # Jogador (preenchido quando torneio é finalizado com resultados)
    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prize_payments'
    )
    
    # Valor monetário
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor em reais a ser pago"
    )
    
    # Percentual (para referência, especialmente em modo PERCENTUAL)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentual do pote total (ex: 50.00 para 50%)"
    )
    
    # Informações de pagamento
    pago = models.BooleanField(default=False, help_text="Se o prêmio foi pago")
    data_pagamento = models.DateTimeField(null=True, blank=True)
    metodo_pagamento = models.CharField(
        max_length=50,
        blank=True,
        help_text="Dinheiro, Pix, Transferência, etc"
    )
    
    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prize_payments_created'
    )
    
    class Meta:
        ordering = ['position']
        verbose_name = "Prêmio por Posição"
        verbose_name_plural = "Prêmios por Posição"
        unique_together = ('prize_structure', 'position')
        indexes = [
            models.Index(fields=['prize_structure', 'position']),
            models.Index(fields=['player', 'pago']),
        ]
    
    def __str__(self):
        lugar = f"{self.position}º lugar"
        valor = f"R$ {self.amount:.2f}".replace('.', ',')
        if self.player:
            return f"{lugar} - {self.player.nome} ({valor})"
        return f"{lugar} - {valor}"
    
    @property
    def posicao_nome(self):
        """Retorna a descrição amigável da posição (1º, 2º, 3º, etc)"""
        suffixes = {1: 'º', 2: 'º', 3: 'º'}
        return f"{self.position}{suffixes.get(self.position, 'º')}"


class PrizeTemplate(models.Model):
    """
    Templates pré-definidos de estrutura de prêmios para reutilização rápida.
    Exemplo: "Top 3 Clássico", "Top 4 Balanceado", etc.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='prize_templates')
    
    # Identificação
    nome = models.CharField(max_length=255, help_text="Ex: 'Top 3 Clássico', 'Top 4 Balanceado'")
    descricao = models.TextField(blank=True, help_text="Descrição e notas sobre quando usar")
    
    # Configuração
    modo = models.CharField(
        max_length=20,
        choices=[
            ('PERCENTUAL', 'Percentual do Pote'),
            ('FIXO', 'Valores Fixos'),
        ],
        default='PERCENTUAL'
    )
    itm_count = models.IntegerField(help_text="Quantas posições são premiadas")
    
    # Dados do template (armazenados como JSON para flexibilidade)
    data = models.JSONField(
        help_text="Array com estrutura de prêmios: "
                  "[{position: 1, percentage: 50, valor_fixo: null}, ...]"
    )
    
    # Controle
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['itm_count', 'nome']
        verbose_name = "Template de Prêmios"
        verbose_name_plural = "Templates de Prêmios"
        unique_together = ('tenant', 'nome')
    
    def __str__(self):
        return f"{self.nome} ({self.itm_count} premiados)"