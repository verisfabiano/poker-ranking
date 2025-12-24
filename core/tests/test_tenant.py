from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from decimal import Decimal
from ..models import Tenant, TenantUser, Season, Player, Tournament, TournamentEntry, TournamentResult, PlayerStatistics
from ..views.ranking import ranking_avancado, _calcular_e_atualizar_stats
from ..middleware.tenant_middleware import TenantMiddleware, set_current_tenant


class TenantIsolationTestCase(TestCase):
    """
    Testa isolamento de dados entre tenants.
    """
    
    def setUp(self):
        """Configura tenants, usuários e dados de teste."""
        # Criar tenants
        self.tenant1 = Tenant.objects.create(nome='Tenant 1', slug='tenant-1')
        self.tenant2 = Tenant.objects.create(nome='Tenant 2', slug='tenant-2')
        
        # Criar usuários
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'pass123')
        
        # Associar usuários a tenants
        TenantUser.objects.create(user=self.user1, tenant=self.tenant1, role='admin')
        TenantUser.objects.create(user=self.user2, tenant=self.tenant2, role='admin')
        
        # Criar seasons
        self.season1 = Season.objects.create(
            nome='Temporada 1',
            tenant=self.tenant1,
            tipo_calculo='FIXO',
            pts_1lugar=100,
            pts_2lugar=80,
            pts_3lugar=60
        )
        self.season2 = Season.objects.create(
            nome='Temporada 2',
            tenant=self.tenant2,
            tipo_calculo='FIXO',
            pts_1lugar=100,
            pts_2lugar=80,
            pts_3lugar=60
        )
        
        # Criar jogadores
        self.player1_t1 = Player.objects.create(
            nome='Jogador 1 T1',
            apelido='J1-T1',
            email='j1t1@test.com',
            tenant=self.tenant1
        )
        self.player2_t1 = Player.objects.create(
            nome='Jogador 2 T1',
            apelido='J2-T1',
            email='j2t1@test.com',
            tenant=self.tenant1
        )
        self.player1_t2 = Player.objects.create(
            nome='Jogador 1 T2',
            apelido='J1-T2',
            email='j1t2@test.com',
            tenant=self.tenant2
        )
        
        # Criar torneios
        self.tournament1_t1 = Tournament.objects.create(
            nome='Torneio 1 T1',
            season=self.season1,
            tenant=self.tenant1,
            buyin=Decimal('10.00'),
            data='2024-01-15'
        )
        self.tournament1_t2 = Tournament.objects.create(
            nome='Torneio 1 T2',
            season=self.season2,
            tenant=self.tenant2,
            buyin=Decimal('10.00'),
            data='2024-01-15'
        )
    
    def test_tenant_isolation_players(self):
        """Verifica se jogadores estão isolados por tenant."""
        players_t1 = Player.objects.filter(tenant=self.tenant1)
        players_t2 = Player.objects.filter(tenant=self.tenant2)
        
        self.assertEqual(players_t1.count(), 2)
        self.assertEqual(players_t2.count(), 1)
        self.assertNotIn(self.player1_t2, players_t1)
    
    def test_tenant_isolation_tournaments(self):
        """Verifica se torneios estão isolados por tenant."""
        tournaments_t1 = Tournament.objects.filter(tenant=self.tenant1)
        tournaments_t2 = Tournament.objects.filter(tenant=self.tenant2)
        
        self.assertEqual(tournaments_t1.count(), 1)
        self.assertEqual(tournaments_t2.count(), 1)
        self.assertNotIn(self.tournament1_t2, tournaments_t1)
    
    def test_user_cannot_access_other_tenant_data(self):
        """Testa que usuário de T1 não vê dados de T2."""
        client = Client()
        client.login(username='user1', password='pass123')
        
        # Simula request para tenant 1
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user1
        
        middleware = TenantMiddleware(lambda r: None)
        middleware.process_request(request)
        
        # User1 deve ter tenant1
        self.assertEqual(request.tenant, self.tenant1)
    
    def test_statistics_isolation(self):
        """Testa que estatísticas são isoladas por tenant."""
        # Criar resultados para tenant 1
        TournamentEntry.objects.create(
            player=self.player1_t1,
            tournament=self.tournament1_t1,
            tenant=self.tenant1
        )
        TournamentResult.objects.create(
            player=self.player1_t1,
            tournament=self.tournament1_t1,
            posicao=1,
            premiacao_recebida=Decimal('50.00'),
            tenant=self.tenant1
        )
        
        # Calcular stats
        stats = _calcular_e_atualizar_stats(self.season1, self.player1_t1, self.tenant1)
        
        # Verificar que stats existem apenas para tenant1
        stats_t1 = PlayerStatistics.objects.filter(
            player=self.player1_t1,
            season=self.season1,
            tenant=self.tenant1
        )
        stats_t2 = PlayerStatistics.objects.filter(
            player=self.player1_t1,
            season=self.season2,
            tenant=self.tenant2
        )
        
        self.assertEqual(stats_t1.count(), 1)
        self.assertEqual(stats_t2.count(), 0)
        self.assertEqual(stats.pontos_totais, 100)


class TenantMiddlewareTestCase(TestCase):
    """
    Testa o middleware de tenant.
    """
    
    def setUp(self):
        self.tenant = Tenant.objects.create(nome='Test Tenant', slug='test-tenant')
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass123')
        TenantUser.objects.create(user=self.user, tenant=self.tenant, role='admin')
        
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: None)
    
    def test_middleware_sets_tenant(self):
        """Testa se middleware define tenant no request."""
        request = self.factory.get('/')
        request.user = self.user
        
        self.middleware.process_request(request)
        
        self.assertIsNotNone(request.tenant)
        self.assertEqual(request.tenant, self.tenant)
    
    def test_middleware_inactive_tenant(self):
        """Testa que tenant inativo não é definido."""
        self.tenant.ativo = False
        self.tenant.save()
        
        request = self.factory.get('/')
        request.user = self.user
        
        self.middleware.process_request(request)
        
        self.assertIsNone(request.tenant)
    
    def test_middleware_cleanup(self):
        """Testa limpeza de tenant após request."""
        request = self.factory.get('/')
        request.user = self.user
        
        self.middleware.process_request(request)
        response = self.middleware.process_response(request, None)
        
        # Verificar que thread local foi limpo
        from ..middleware.tenant_middleware import get_current_tenant
        self.assertIsNone(get_current_tenant())


class TenantRolePermissionsTestCase(TestCase):
    """
    Testa permissões baseadas em role.
    """
    
    def setUp(self):
        self.tenant = Tenant.objects.create(nome='Test Tenant', slug='test-tenant')
        
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass123')
        self.player_user = User.objects.create_user('player', 'player@test.com', 'pass123')
        
        TenantUser.objects.create(user=self.admin_user, tenant=self.tenant, role='admin')
        TenantUser.objects.create(user=self.player_user, tenant=self.tenant, role='player')
    
    def test_admin_can_manage_tenant(self):
        """Testa que admin tem permissão."""
        tenant_user = TenantUser.objects.get(user=self.admin_user, tenant=self.tenant)
        self.assertEqual(tenant_user.role, 'admin')
    
    def test_player_cannot_manage_tenant(self):
        """Testa que player não tem permissão de admin."""
        tenant_user = TenantUser.objects.get(user=self.player_user, tenant=self.tenant)
        self.assertEqual(tenant_user.role, 'player')
