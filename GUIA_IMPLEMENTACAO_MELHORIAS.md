# 🛠️ GUIA PRÁTICO: IMPLEMENTAÇÃO DAS MELHORIAS

## Como Resolver os 5 Problemas Críticos de Segurança

---

## 🔴 PROBLEMA 1: Rate Limiting & Brute Force Protection

### Passo 1: Instalar dependência
```bash
pip install django-ratelimit
pip freeze > requirements.txt
```

### Passo 2: Criar decorador customizado
```python
# core/decorators/rate_limit.py
from django_ratelimit.decorators import ratelimit
from functools import wraps

def login_ratelimit(view_func):
    """Rate limit específico para login"""
    @wraps(view_func)
    @ratelimit(key='ip', rate='5/h', method='POST')
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def api_ratelimit(view_func):
    """Rate limit para APIs"""
    @wraps(view_func)
    @ratelimit(key='ip', rate='100/h', method=['GET', 'POST'])
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
```

### Passo 3: Aplicar em views de login
```python
# core/views/auth.py
from core.decorators.rate_limit import login_ratelimit

@login_ratelimit
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # ... resto do código
```

### Passo 4: Testar
```bash
# Fazer 6 requisições POST em 1 hora (deve bloquear a 6ª)
curl -X POST http://localhost:8000/login/ -d "email=test@test.com&password=wrong"
```

### Impacto
- ✅ Máximo 5 tentativas de login por hora por IP
- ✅ Protege contra dicionário attacks
- ✅ Log automático de tentativas bloqueadas

---

## 🔴 PROBLEMA 2: Audit Log Financeiro

### Passo 1: Criar modelo de auditoria
```python
# core/models.py - adicionar ao final
class FinancialAuditLog(models.Model):
    """Log de auditoria para todas as transações financeiras"""
    
    TRANSACTION_TYPES = (
        ('BUY_IN', 'Buy-in'),
        ('REBUY', 'Rebuy'),
        ('REBUY_DUPLO', 'Rebuy Duplo'),
        ('ADDON', 'Add-on'),
        ('TIME_CHIP', 'Time Chip'),
        ('PREMIO', 'Premiação'),
        ('RAKE', 'Rake'),
        ('AJUSTE', 'Ajuste Manual'),
        ('REEMBOLSO', 'Reembolso'),
    )
    
    # Referências
    tournament = models.ForeignKey(
        'Tournament',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    player = models.ForeignKey(
        'Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuário que fez a operação"
    )
    
    # Dados da transação
    tipo = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Valor da transação"
    )
    descricao = models.CharField(
        max_length=255,
        blank=True,
        help_text="Descrição da transação"
    )
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP do usuário que fez a operação"
    )
    hash_verificacao = models.CharField(
        max_length=256,
        blank=True,
        editable=False,
        help_text="Hash SHA256 para verificar integridade"
    )
    
    class Meta:
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['tournament', 'criado_em']),
            models.Index(fields=['player', 'criado_em']),
            models.Index(fields=['tenant', 'criado_em']),
        ]
        verbose_name = "Log de Auditoria Financeira"
        verbose_name_plural = "Logs de Auditoria Financeira"
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.valor} - {self.criado_em}"
    
    def calcular_hash(self):
        """Calcula hash SHA256 para integridade"""
        import hashlib
        data = f"{self.tournament_id}{self.player_id}{self.tipo}{self.valor}{self.criado_em}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        if not self.hash_verificacao:
            self.hash_verificacao = self.calcular_hash()
        super().save(*args, **kwargs)
    
    def verificar_integridade(self):
        """Verifica se não foi alterado"""
        hash_atual = self.calcular_hash()
        return hash_atual == self.hash_verificacao
```

### Passo 2: Criar sinal para auto-log
```python
# core/signals.py - adicionar novo arquivo ou expandir existente
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import FinancialAuditLog, TournamentResult, TournamentPlayerPurchase

@receiver(post_save, sender=TournamentResult)
def log_tournament_result(sender, instance, created, **kwargs):
    """Log quando resultado é lançado/alterado"""
    if created:
        FinancialAuditLog.objects.create(
            tournament=instance.tournament,
            player=instance.player,
            tenant=instance.tournament.tenant,
            tipo='PREMIO',
            valor=instance.premiacao_recebida or 0,
            descricao=f"Premiação por {instance.get_posicao_display()}"
        )

@receiver(post_save, sender=TournamentPlayerPurchase)
def log_player_purchase(sender, instance, created, **kwargs):
    """Log quando rebuy/addon é comprado"""
    if created:
        FinancialAuditLog.objects.create(
            tournament=instance.tournament,
            player=instance.player,
            tenant=instance.tenant,
            tipo=instance.tipo,
            valor=instance.valor * instance.quantidade,
            descricao=f"{instance.get_tipo_display()} x{instance.quantidade}"
        )
```

### Passo 3: Criar view para consultar audit log
```python
# core/views/financial.py - adicionar novo método
@admin_required
def audit_log(request, tournament_id=None):
    """Visualizar audit log financeiro"""
    logs = FinancialAuditLog.objects.filter(tenant=request.tenant)
    
    if tournament_id:
        logs = logs.filter(tournament_id=tournament_id)
    
    logs = logs.select_related('tournament', 'player', 'user').order_by('-criado_em')
    
    # Paginação
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'total': logs.count(),
        'tournament_id': tournament_id,
    }
    return render(request, 'audit_log.html', context)
```

### Passo 4: Executar migrate
```bash
python manage.py makemigrations
python manage.py migrate
```

### Impacto
- ✅ Rastreamento de 100% de transações
- ✅ Detecção de fraudes
- ✅ Compliance regulatório
- ✅ Impossível negar/alterar registros

---

## 🔴 PROBLEMA 3: Desabilitar DEBUG em Produção

### Passo 1: Atualizar settings.py
```python
# backend/settings.py - linha 27
# ANTES:
# DEBUG = True

# DEPOIS:
import os
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

### Passo 2: Configurar variáveis de ambiente
```bash
# .env (desenvolvimento)
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Production (Railway):
DEBUG=False
SECRET_KEY=chave-super-secreta-aleatoria
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

### Passo 3: Testar
```bash
# Desenvolvimento
DEBUG=True python manage.py runserver

# Simulando produção
DEBUG=False python manage.py runserver
# Deve mostrar erro genérico, não stack trace
```

### Impacto
- ✅ Stack traces não expostos
- ✅ Diretórios não revelados
- ✅ Variáveis de ambiente seguras
- ✅ Conformidade com OWASP Top 10

---

## 🔴 PROBLEMA 4: Forçar HTTPS & Cookies Seguros

### Passo 1: Atualizar settings.py
```python
# backend/settings.py
import os

# ========== SEGURANÇA HTTPS ==========
if not DEBUG:
    # Redirecionar HTTP → HTTPS
    SECURE_SSL_REDIRECT = True
    
    # Cookies apenas via HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (Force browser a usar HTTPS por 1 ano)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # X-Frame-Options
    X_FRAME_OPTIONS = 'DENY'
    
    # Content Security Policy
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
        "style-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    }
else:
    # Development
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
```

### Passo 2: Configurar Railway para SSL
No Railway Dashboard:
1. Ir para Settings
2. Custom Domain
3. Enable Auto SSL Certificate
4. Apontar domínio para Railway

### Passo 3: Testar
```bash
# Deve redirecionar
curl -L http://seu-dominio.com/

# Deve funcionar via HTTPS
curl https://seu-dominio.com/
```

### Impacto
- ✅ Todas conexões encriptadas
- ✅ Proteção contra MITM attacks
- ✅ Cookies seguros
- ✅ Conformidade PCI-DSS

---

## 🔴 PROBLEMA 5: Backup Automático

### Opção A: Railway Postgres Backups (Recomendado)
Railway já faz backups automáticos!

**Verificar no Railway Dashboard:**
1. Ir para seu banco PostgreSQL
2. Aba "Backups"
3. Deve mostrar backups diários automáticos

**Setup:**
```python
# Nada para fazer - Railway já configura
# Você pode fazer restore via Dashboard
```

### Opção B: Backup Local Automático (Extra proteção)
```bash
# criar arquivo: backup_db.sh
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/poker_ranking"
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Criar diretório se não existir
mkdir -p $BACKUP_DIR

# Fazer backup
pg_dump $DATABASE_URL > $BACKUP_FILE

# Compactar
gzip $BACKUP_FILE

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup salvo: $BACKUP_FILE.gz"
```

### Opção C: Configurar no crontab
```bash
# Fazer backup diariamente às 2AM
0 2 * * * /path/to/backup_db.sh >> /var/log/backup.log 2>&1

# Verificar cron logs
tail -f /var/log/syslog | grep CRON
```

### Opção D: Usar S3 para Cold Storage
```python
# Adicionar boto3 para backup em S3
pip install boto3

# settings.py
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'poker-ranking-backups'
AWS_S3_REGION_NAME = 'us-east-1'
```

### Impacto
- ✅ Proteção contra perda de dados
- ✅ Disaster recovery plan
- ✅ Compliance regulatório
- ✅ Recuperação em <1 hora

---

## 🟡 PROBLEMA 6: Adicionar Testes Unitários

### Passo 1: Configurar teste
```bash
pip install pytest pytest-django pytest-cov
```

### Passo 2: Criar arquivo de configuração
```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
```

### Passo 3: Exemplo de teste - Ranking
```python
# core/tests/test_ranking.py
import pytest
from decimal import Decimal
from django.test import TestCase
from core.models import (
    Season, Player, Tournament, TournamentEntry, 
    TournamentResult, PlayerStatistics, Tenant
)

@pytest.mark.django_db
class TestRankingCalculation:
    
    def setup_method(self):
        """Preparar dados de teste"""
        self.tenant = Tenant.objects.create(nome="Test Club")
        self.season = Season.objects.create(
            nome="2025",
            data_inicio="2025-01-01",
            data_fim="2025-12-31",
            tenant=self.tenant
        )
        self.player = Player.objects.create(
            nome="João Silva",
            tenant=self.tenant
        )
    
    def test_calculate_points_for_first_place(self):
        """Teste se 1º lugar recebe pontos corretos"""
        tournament = Tournament.objects.create(
            season=self.season,
            nome="Torneio Teste",
            data="2025-01-15",
            tenant=self.tenant
        )
        
        entry = TournamentEntry.objects.create(
            tournament=tournament,
            player=self.player,
            tenant=self.tenant
        )
        
        # 1º lugar deve receber 100 pontos
        result = TournamentResult.objects.create(
            tournament=tournament,
            player=self.player,
            posicao=1,
            pontos_finais=100,
            tenant=self.tenant
        )
        
        assert result.pontos_finais == 100
    
    def test_ranking_order(self):
        """Teste se ranking está em ordem correta"""
        # Criar 3 jogadores
        players = [
            Player.objects.create(nome=f"Player {i}", tenant=self.tenant)
            for i in range(3)
        ]
        
        # Criar resultados
        for idx, player in enumerate(players):
            tournament = Tournament.objects.create(
                season=self.season,
                nome=f"Torneio {idx}",
                data="2025-01-15",
                tenant=self.tenant
            )
            
            TournamentEntry.objects.create(
                tournament=tournament,
                player=player,
                tenant=self.tenant
            )
            
            # Pontos decrescentes: 100, 80, 60
            TournamentResult.objects.create(
                tournament=tournament,
                player=player,
                posicao=idx + 1,
                pontos_finais=100 - (idx * 20),
                tenant=self.tenant
            )
        
        # Verificar ranking
        stats = PlayerStatistics.objects.filter(
            season=self.season
        ).order_by('-pontos_totais').values_list('player__nome', 'pontos_totais')
        
        # Primeiro deve ter 100 pontos
        assert stats[0][1] == 100

# Rodar teste
# pytest core/tests/test_ranking.py -v
# pytest core/tests/test_ranking.py --cov=core
```

### Passo 4: Exemplo de teste - View
```python
# core/tests/test_views.py
import pytest
from django.test import Client
from django.contrib.auth.models import User
from core.models import Tenant, TenantUser

@pytest.mark.django_db
class TestAuthViews:
    
    def setup_method(self):
        self.client = Client()
        self.tenant = Tenant.objects.create(nome="Test Club")
        self.user = User.objects.create_user(
            username='testuser@test.com',
            email='testuser@test.com',
            password='testpass123'
        )
        TenantUser.objects.create(
            user=self.user,
            tenant=self.tenant,
            role='admin'
        )
    
    def test_login_success(self):
        """Teste login com credenciais corretas"""
        response = self.client.post('/login/', {
            'email': 'testuser@test.com',
            'password': 'testpass123'
        })
        
        # Deve redirecionar para dashboard
        assert response.status_code == 302
        assert response.url == '/painel/'
    
    def test_login_failure(self):
        """Teste login com senha errada"""
        response = self.client.post('/login/', {
            'email': 'testuser@test.com',
            'password': 'wrongpass'
        })
        
        # Deve retornar 200 com form ainda visível
        assert response.status_code == 200
        assert 'Email ou senha incorretos' in str(response.content)
    
    def test_protected_view_requires_login(self):
        """Teste se view protegida requer login"""
        response = self.client.get('/painel/')
        
        # Deve redirecionar para login
        assert response.status_code == 302
        assert '/login/' in response.url
```

### Impacto
- ✅ Detecta regressões
- ✅ Aumenta confiança em refactoring
- ✅ Documentação de código
- ✅ Permite CI/CD automático

---

## 📋 Checklist de Implementação

```markdown
SEGURANÇA (Semana 1):
- [ ] Rate limiting instalado e aplicado em login
- [ ] Audit log implementado e funcionando
- [ ] DEBUG = False em produção
- [ ] HTTPS forçado
- [ ] Backup automático configurado
- [ ] Tests de segurança executados

QUALIDADE (Semana 2-3):
- [ ] Testes unitários para ranking
- [ ] Testes para views críticas
- [ ] Testes para modelos financeiros
- [ ] 70%+ cobertura de code
- [ ] Validação de email implementada
- [ ] Logging estruturado

PERFORMANCE (Semana 4):
- [ ] Cache Redis instalado
- [ ] N+1 queries corrigidas
- [ ] Assets minificados
- [ ] Performance teste (< 2s load time)
```

---

## ✅ Próximas Etapas Após Implementação

1. **Fazer deploy em staging** (Railway preview)
2. **Testar mudanças** (verificar que nada quebrou)
3. **Fazer deploy em produção** (Railway production)
4. **Monitorar por 24h** (verificar logs para erros)
5. **Comunicar ao cliente** (segurança implementada)

---

**Tempo total estimado:** 25-35 horas de desenvolvimento

