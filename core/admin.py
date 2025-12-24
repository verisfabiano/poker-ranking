from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Season,
    Player,
    Tournament,
    TournamentEntry,
    TournamentResult,
    PlayerStatistics,
    PlayerAchievement,
    SeasonInitialPoints,
    TenantUser,
    Tenant,
    TournamentProduct,
    PlayerProductPurchase,
    TournamentType,
    BlindStructure,
    PrizeStructure,
    PrizePayment,
    PrizeTemplate,
)


class TenantFilteredAdmin(admin.ModelAdmin):
    """
    Admin base que filtra automaticamente por tenant do usuário.
    """
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filtra por tenants do usuário
        tenant_ids = TenantUser.objects.filter(user=request.user).values_list('tenant_id', flat=True)
        return qs.filter(tenant_id__in=tenant_ids)
    
    def save_model(self, request, obj, form, change):
        if not change:
            # Se é novo, pega o primeiro tenant do usuário
            if not hasattr(obj, 'tenant') or not obj.tenant:
                tenant_user = TenantUser.objects.filter(user=request.user).first()
                if tenant_user:
                    obj.tenant = tenant_user.tenant
        super().save_model(request, obj, form, change)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'status_badge', 'logo_preview', 'total_usuarios', 'criado_em')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ('criado_em', 'logo_preview')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao', 'logo', 'logo_preview', 'ativo')
        }),
        ('Contato do Clube', {
            'fields': ('club_email', 'club_phone', 'club_cnpj', 'club_website'),
            'classes': ('collapse',)
        }),
        ('Endereço', {
            'fields': ('address_cep', 'address_street', 'address_number', 'address_complement', 
                      'address_neighborhood', 'address_city', 'address_state'),
            'classes': ('collapse',)
        }),
        ('Administrador', {
            'fields': ('admin_full_name', 'admin_phone', 'admin_cpf', 'admin_role'),
            'classes': ('collapse',)
        }),
        ('Limites', {
            'fields': ('max_jogadores', 'max_torneios'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.ativo:
            return format_html('<span style="color: green;">✓ Ativo</span>')
        return format_html('<span style="color: red;">✗ Inativo</span>')
    status_badge.short_description = 'Status'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: contain; border-radius: 4px;" />',
                obj.logo.url
            )
        return '—'
    logo_preview.short_description = 'Prévia da Logo'
    
    def total_usuarios(self, obj):
        return obj.users.count()
    total_usuarios.short_description = 'Usuários'


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role', 'adicionado_em')
    list_filter = ('role', 'tenant', 'adicionado_em')
    search_fields = ('user__username', 'tenant__nome')
    readonly_fields = ('adicionado_em',)
    
    fieldsets = (
        ('Relacionamentos', {
            'fields': ('user', 'tenant')
        }),
        ('Permissões', {
            'fields': ('role',)
        }),
        ('Auditoria', {
            'fields': ('adicionado_em',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            tenant_ids = TenantUser.objects.filter(user=request.user).values_list('tenant_id', flat=True)
            qs = qs.filter(tenant_id__in=tenant_ids)
        return qs


@admin.register(Season)
class SeasonAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'tenant', 'data_inicio', 'ativo')
    list_filter = ('ativo', 'tenant', 'data_inicio')
    search_fields = ('nome',)


@admin.register(Player)
class PlayerAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'apelido', 'tenant', 'email', 'ativo')
    list_filter = ('ativo', 'tenant')
    search_fields = ('nome', 'apelido', 'email')


@admin.register(Tournament)
class TournamentAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'tenant', 'season', 'data', 'buyin', 'status_protecao')
    list_filter = ('tenant', 'season', 'data', 'status')
    search_fields = ('nome',)
    
    def status_protecao(self, obj):
        """Mostra se o torneio está protegido contra exclusão"""
        from core.models import TournamentResult, TournamentEntry, TournamentPlayerPurchase, TournamentPrize
        
        has_results = TournamentResult.objects.filter(tournament=obj).exists()
        has_entries = TournamentEntry.objects.filter(tournament=obj).exists()
        has_purchases = TournamentPlayerPurchase.objects.filter(tournament=obj).exists()
        has_prizes = TournamentPrize.objects.filter(tournament=obj).exists()
        
        if has_results or has_entries or has_purchases or has_prizes:
            return '🔒 Protegido'
        return '✓ Livre'
    
    status_protecao.short_description = 'Proteção'
    
    def get_actions(self, request):
        """Remove ação de exclusão em massa"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        """Verifica permissão de exclusão individual"""
        if obj is None:
            return True
        
        from core.models import TournamentResult, TournamentEntry, TournamentPlayerPurchase, TournamentPrize
        
        # Se tem qualquer tipo de dado associado, nega permissão
        if (TournamentResult.objects.filter(tournament=obj).exists() or
            TournamentEntry.objects.filter(tournament=obj).exists() or
            TournamentPlayerPurchase.objects.filter(tournament=obj).exists() or
            TournamentPrize.objects.filter(tournament=obj).exists()):
            return False
        
        return True


@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(TenantFilteredAdmin):
    list_display = ('player', 'season', 'tenant', 'pontos_totais', 'vitórias', 'roi')
    list_filter = ('tenant', 'season')
    search_fields = ('player__nome', 'player__apelido')
    readonly_fields = ('pontos_totais', 'media_pontos', 'roi', 'taxa_itm')


@admin.register(TournamentEntry)
class TournamentEntryAdmin(TenantFilteredAdmin):
    list_display = ('player', 'tournament', 'tenant', 'data_inscricao')
    list_filter = ('tournament', 'tenant', 'data_inscricao')
    search_fields = ('player__nome', 'tournament__nome')


@admin.register(TournamentResult)
class TournamentResultAdmin(TenantFilteredAdmin):
    list_display = ('player', 'tournament', 'tenant', 'posicao', 'pontos_finais', 'premiacao_recebida')
    list_filter = ('tournament', 'tenant', 'posicao')
    search_fields = ('player__nome', 'tournament__nome')


@admin.register(SeasonInitialPoints)
class SeasonInitialPointsAdmin(TenantFilteredAdmin):
    list_display = ('season', 'player', 'tenant', 'pontos_iniciais')
    list_filter = ('season', 'tenant')
    search_fields = ('player__nome',)


@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(TenantFilteredAdmin):
    list_display = ('season', 'player', 'tenant', 'tipo', 'obtido_em')
    list_filter = ('season', 'tenant', 'tipo', 'obtido_em')
    search_fields = ('player__nome',)


@admin.register(TournamentType)
class TournamentTypeAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'tenant', 'buyin_padrao', 'rake_padrao')
    list_filter = ('tenant',)
    search_fields = ('nome',)


@admin.register(BlindStructure)
class BlindStructureAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'tenant', 'total_niveis')
    list_filter = ('tenant',)
    search_fields = ('nome',)
    
    def total_niveis(self, obj):
        return obj.levels.count()
    total_niveis.short_description = 'Níveis'


@admin.register(TournamentProduct)
class TournamentProductAdmin(TenantFilteredAdmin):
    """
    Admin para gerenciar produtos adicionais oferecidos aos jogadores.
    Ex: Jack Pot, Staff, Bounty, etc.
    """
    list_display = ('nome', 'tenant', 'valor_formatado', 'premiacao_status', 'descricao_curta')
    list_filter = ('tenant', 'entra_em_premiacao')
    search_fields = ('nome', 'descricao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tenant', 'valor')
        }),
        ('Configuração', {
            'fields': ('entra_em_premiacao',),
            'description': 'Marque se este produto entra no cálculo de premiação'
        }),
        ('Descrição', {
            'fields': ('descricao',)
        }),
    )
    
    def valor_formatado(self, obj):
        return f'R$ {obj.valor:.2f}'
    valor_formatado.short_description = 'Valor'
    
    def premiacao_status(self, obj):
        if obj.entra_em_premiacao:
            return '✅ Entra'
        return '❌ Não entra'
    premiacao_status.short_description = 'Premiação'
    
    def descricao_curta(self, obj):
        if obj.descricao:
            return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao
        return '-'
    descricao_curta.short_description = 'Descrição'


@admin.register(PlayerProductPurchase)
class PlayerProductPurchaseAdmin(TenantFilteredAdmin):
    """
    Admin para registrar compras de produtos adicionais pelos jogadores.
    Rastreia: Jack Pot, Staff, Bounty, Rebuys, Add-ons, etc.
    """
    list_display = ('player', 'tournament', 'product', 'quantidade', 'valor_pago_formatado', 'tenant')
    list_filter = ('tenant', 'tournament', 'product__nome', 'player')
    search_fields = ('player__nome', 'tournament__nome', 'product__nome')
    readonly_fields = ('tenant',)
    
    fieldsets = (
        ('Relacionamentos', {
            'fields': ('tournament', 'player', 'product', 'tenant')
        }),
        ('Compra', {
            'fields': ('quantidade', 'valor_pago')
        }),
    )
    
    def valor_pago_formatado(self, obj):
        return f'R$ {obj.valor_pago:.2f}'
    valor_pago_formatado.short_description = 'Valor Pago'
    
    def save_model(self, request, obj, form, change):
        if not change:
            if not hasattr(obj, 'tenant') or not obj.tenant:
                tenant_user = TenantUser.objects.filter(user=request.user).first()
                if tenant_user:
                    obj.tenant = tenant_user.tenant
        super().save_model(request, obj, form, change)


# ============================================================
#  SISTEMA DE PREMIAÇÃO
# ============================================================

class PrizePaymentInline(admin.TabularInline):
    model = PrizePayment
    extra = 0
    fields = ('position', 'player', 'amount', 'percentage', 'pago')
    readonly_fields = ('position',)


@admin.register(PrizeStructure)
class PrizeStructureAdmin(TenantFilteredAdmin):
    list_display = ('tournament', 'modo_badge', 'itm_count', 'total_prize_pool_formatted', 'status_badge', 'criado_em')
    list_filter = ('modo', 'finalizado', 'criado_em')
    search_fields = ('tournament__nome',)
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [PrizePaymentInline]
    
    fieldsets = (
        ('Torneio', {
            'fields': ('tournament', 'tenant')
        }),
        ('Configuração', {
            'fields': ('modo', 'itm_count', 'total_prize_pool')
        }),
        ('Controle', {
            'fields': ('finalizado', 'criado_por', 'criado_em', 'atualizado_em')
        }),
    )
    
    def modo_badge(self, obj):
        colors = {'PERCENTUAL': '#0066cc', 'FIXO': '#666600'}
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.modo, '#999999'),
            obj.get_modo_display()
        )
    modo_badge.short_description = 'Modo'
    
    def total_prize_pool_formatted(self, obj):
        return f'R$ {obj.total_prize_pool:.2f}'
    total_prize_pool_formatted.short_description = 'Pote Total'
    
    def status_badge(self, obj):
        if obj.finalizado:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Finalizado</span>')
        return format_html('<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">◌ Em Edição</span>')
    status_badge.short_description = 'Status'


@admin.register(PrizePayment)
class PrizePaymentAdmin(admin.ModelAdmin):
    list_display = ('position', 'player_or_empty', 'amount_formatted', 'percentage_display', 'pago_badge')
    list_filter = ('pago', 'prize_structure__tournament__season', 'criado_em')
    search_fields = ('player__nome', 'prize_structure__tournament__nome')
    readonly_fields = ('criado_em',)
    
    fieldsets = (
        ('Posição', {
            'fields': ('prize_structure', 'position')
        }),
        ('Jogador (Opcional)', {
            'fields': ('player',)
        }),
        ('Valores', {
            'fields': ('amount', 'percentage')
        }),
        ('Pagamento', {
            'fields': ('pago', 'data_pagamento', 'metodo_pagamento')
        }),
        ('Controle', {
            'fields': ('criado_por', 'criado_em')
        }),
    )
    
    def player_or_empty(self, obj):
        return obj.player.nome if obj.player else '---'
    player_or_empty.short_description = 'Jogador'
    
    def amount_formatted(self, obj):
        return f'R$ {obj.amount:.2f}'
    amount_formatted.short_description = 'Prêmio'
    
    def percentage_display(self, obj):
        return f'{obj.percentage:.2f}%' if obj.percentage else '---'
    percentage_display.short_description = 'Percentual'
    
    def pago_badge(self, obj):
        if obj.pago:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Pago</span>')
        return format_html('<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">◌ Pendente</span>')
    pago_badge.short_description = 'Pagamento'


@admin.register(PrizeTemplate)
class PrizeTemplateAdmin(TenantFilteredAdmin):
    list_display = ('nome', 'modo', 'itm_count', 'ativo_badge', 'atualizado_em')
    list_filter = ('modo', 'ativo', 'itm_count', 'atualizado_em')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em', 'data_preview')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('tenant', 'nome', 'descricao')
        }),
        ('Configuração', {
            'fields': ('modo', 'itm_count')
        }),
        ('Dados do Template', {
            'fields': ('data', 'data_preview')
        }),
        ('Status', {
            'fields': ('ativo', 'criado_em', 'atualizado_em')
        }),
    )
    
    def data_preview(self, obj):
        if not obj.data:
            return '---'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f8f9fa;"><th style="border: 1px solid #ddd; padding: 8px;">Pos</th><th style="border: 1px solid #ddd; padding: 8px;">%</th><th style="border: 1px solid #ddd; padding: 8px;">Fixo</th></tr>'
        
        for item in obj.data:
            html += '<tr>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px;">{item.get("position")}º</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px;">{item.get("percentage", "---")}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px;">R$ {item.get("valor_fixo", "---")}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    data_preview.short_description = 'Preview'
    
    def ativo_badge(self, obj):
        if obj.ativo:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Ativo</span>')
        return format_html('<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">✗ Inativo</span>')
    ativo_badge.short_description = 'Status'
