# 🔧 PokerClube - Documentação Técnica Detalhada

## 1. Arquitetura do Sistema

### Estrutura de Camadas

```
┌─────────────────────────────────────────┐
│     FRONTEND (Template + JavaScript)    │
│  - Bootstrap 5 Responsive Design        │
│  - jQuery para interações               │
│  - Gráficos com Chart.js                │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         DJANGO REST API LAYER           │
│  - Views baseadas em classes/funções   │
│  - JSON Responses                       │
│  - Decoradores de autenticação          │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│      BUSINESS LOGIC (Core Apps)        │
│  - Models de domínio                    │
│  - Decoradores customizados             │
│  - Managers de banco de dados           │
│  - Signals para eventos                 │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│    PERSISTENCE LAYER (ORM Django)       │
│  - PostgreSQL/SQLite                    │
│  - Migrations automáticas               │
│  - Relacionamentos foreignkey/many-to-m │
└─────────────────────────────────────────┘
```

### Componentes Principais

#### Backend (`/backend/`)
```
backend/
├── settings.py          # Configurações gerais
├── urls.py             # URL patterns globais
├── asgi.py             # Async interface
└── wsgi.py             # WSGI interface (produção)
```

#### Core App (`/core/`)
```
core/
├── models.py                    # Modelos de dados
├── admin.py                     # Admin interface
├── signals.py                   # Event handlers
├── urls.py                      # URLs do app
├── views/                       # Lógica de negócio
│   ├── player.py               # Views de jogador
│   ├── tournament.py           # Gerenciar torneios
│   ├── ranking.py              # Cálculo de ranking
│   ├── season.py               # Temporadas
│   ├── auth.py                 # Autenticação
│   ├── financial.py            # Finanças
│   └── ...
├── middleware/                  # Middlewares customizados
│   ├── tenant_middleware.py    # Multi-tenant
│   └── subdomain_middleware.py # Subdomínio
├── decorators/                  # Decoradores
│   └── tenant_decorators.py    # @tenant_required
├── managers/                    # Managers de modelo
│   └── tenant_manager.py       # Operações de tenant
├── migrations/                  # Histórico de mudanças DB
├── fixtures/                    # Dados iniciais
├── templates/                   # Templates HTML
└── static/                      # CSS, JS, imagens
```

---

## 2. Modelos de Dados

### Hierarquia de Relacionamentos

```
Tenant (Club)
├── Season (Temporada)
│   ├── Tournament (Torneio)
│   │   ├── TournamentEntry (Inscrição)
│   │   │   └── TournamentResult (Resultado)
│   │   └── TournamentType (Tipo)
│   ├── Player (Jogador)
│   │   ├── TournamentEntry
│   │   └── PlayerStatistics
│   └── BlindStructure (Estrutura de Blinds)
│
└── TenantUser (Acesso)
    ├── User (Django Auth)
    └── Role (admin/player/moderator)
```

### Modelos Principais

#### Tenant
```python
class Tenant(models.Model):
    nome = CharField()           # Nome do clube
    slug = SlugField(unique=True)
    ativo = BooleanField(default=True)
    descricao = TextField()
    logo = ImageField()
    # ... outros campos
```
**Uso**: Isolamento de dados entre múltiplos clubes

#### Player
```python
class Player(models.Model):
    user = OneToOneField(User)    # Link com Django User
    nome = CharField()
    apelido = CharField()
    email = EmailField()
    tenant = ForeignKey(Tenant)
    status = CharField(choices=STATUS_CHOICES)
    # ... campos adicionais
```
**Uso**: Representação de um jogador do clube

#### Tournament
```python
class Tournament(models.Model):
    nome = CharField()
    season = ForeignKey(Season)
    data = DateTimeField()
    buyin = DecimalField()        # Valor de entrada
    permite_rebuy = BooleanField()
    permite_addon = BooleanField()
    rake_type = CharField(choices=RAKE_CHOICES)
    # ... configuração de blinds, rake, etc
```
**Uso**: Definição de um torneio específico

#### TournamentEntry
```python
class TournamentEntry(models.Model):
    tournament = ForeignKey(Tournament)
    player = ForeignKey(Player)
    confirmou_presenca = BooleanField()
    confirmado_pelo_admin = BooleanField()
    pontos_participacao = IntegerField()
```
**Uso**: Registro de inscrição de um jogador em um torneio

#### TournamentResult
```python
class TournamentResult(models.Model):
    tournament = ForeignKey(Tournament)
    player = ForeignKey(Player)
    posicao = IntegerField()       # Colocação final
    premiacao_recebida = DecimalField()
    pontos_base = IntegerField()
    pontos_bonus = IntegerField()
```
**Uso**: Resultado final de um jogador em um torneio

#### PlayerStatistics
```python
class PlayerStatistics(models.Model):
    player = ForeignKey(Player)
    season = ForeignKey(Season)
    pontos_totais = IntegerField()
    vitórias = IntegerField()      # 1º lugares
    top_3 = IntegerField()
    top_10 = IntegerField()
    participacoes = IntegerField()
```
**Uso**: Cache agregado de estatísticas para ranking rápido

#### TenantUser
```python
class TenantUser(models.Model):
    user = ForeignKey(User)
    tenant = ForeignKey(Tenant)
    role = CharField(choices=ROLE_CHOICES)  # admin/player
```
**Uso**: Vincular usuário a tenant com role específico

---

## 3. Fluxos de Dados Principais

### Fluxo 1: Inscrição em Torneio

```
Jogador acessa portal
    ↓
View: player_tournaments (autenticado + tenant_required)
    ↓
Busca tournaments AGENDADO não inscrito
    ↓
Renderiza lista com botão "Inscrever"
    ↓
POST confirmando inscrição
    ↓
Cria TournamentEntry (pendente confirmação admin)
    ↓
Redirect com confirmação
    ↓
Admin aprova inscrição no tournament_entries_manage
    ↓
TournamentEntry.confirmado_pelo_admin = True
```

### Fluxo 2: Lançamento de Resultado

```
Admin acessa tournament_results (admin_required)
    ↓
Busca todas as TournamentEntry CONFIRMADAS
    ↓
Renderiza formulário com posições
    ↓
Admin coloca posição e calcula prêmios
    ↓
POST com dados
    ↓
Cria/atualiza TournamentResult
    ↓
Calcula pontos automaticamente (usar _calcular_pontos_resultado)
    ↓
Atualiza PlayerStatistics (chamar _calcular_e_atualizar_stats)
    ↓
Atualiza Ranking (ordena por pontos_totais)
```

### Fluxo 3: Visualização de Dashboard

```
Jogador acessa /jogador/home/
    ↓
@login_required (verifica autenticação)
    ↓
@tenant_required (extrai tenant do TenantUser)
    ↓
View: player_home()
    ↓
Busca Player vinculado ao user
    ↓
Calcula estatísticas:
  - Busca TournamentEntry do jogador
  - Soma buy-ins = gasto_total
  - Busca TournamentResult do jogador
  - Soma premiacao_recebida = ganho_total
  - Calcula ROI
  ↓
Busca PlayerStatistics para ranking
    ↓
Renderiza template com dados
```

---

## 4. Sistema de Autenticação

### Decoradores de Acesso

```python
@login_required                    # User autenticado
@tenant_required                   # Com acesso ao tenant correto
@admin_required                    # Staff ou superuser
@player_required                   # Jogador (not staff/superuser)
```

### Fluxo de Login

```
GET /jogador/login/ → player_login.html (form)
    ↓
POST email + senha
    ↓
User.authenticate(email, password)
    ↓
TenantUser.objects.get(user=user) [valida acesso]
    ↓
login(request, user) [seta session]
    ↓
if admin:  redirect('/painel/')
else:      redirect('/jogador/home/')
```

### Middleware de Tenant

```python
# TenantMiddleware.process_request()
1. request.tenant = None
2. if user.is_authenticated:
3.   tenant_user = TenantUser.get(user=user)
4.   request.tenant = tenant_user.tenant
5.   set_current_tenant(tenant_user.tenant)
```

**Resultado**: Toda view tem `request.tenant` automaticamente

---

## 5. Cálculos de Ranking

### Fórmula de Pontos

```
Total = Pontos Base + Pontos Bônus + Ajustes Deal

Onde:
- Pontos Base = Configurável por tipo de torneio
- Pontos Bônus = Multiplicador por posição final
  - 1º lugar: +100%
  - Top 3: +50%
  - Top 10: +25%
- Ajustes Deal = Dividir pontos entre jogadores em deal
```

### Atualização de PlayerStatistics

```python
def _calcular_e_atualizar_stats(season, player, tenant):
    results = TournamentResult.objects.filter(
        season=season,
        player=player,
        tournament__tenant=tenant
    )
    
    stats, created = PlayerStatistics.objects.get_or_create(
        season=season,
        player=player,
        tenant=tenant
    )
    
    stats.participacoes = results.count()
    stats.vitórias = results.filter(posicao=1).count()
    stats.top_3 = results.filter(posicao__lte=3).count()
    stats.top_10 = results.filter(posicao__lte=10).count()
    stats.pontos_totais = results.aggregate(Sum('pontos_finais'))
    
    stats.save()
```

---

## 6. Integração Financeira

### Cálculo de Receita

```
Receita Total = (Buy-in * Participantes) + (Rebuy * Qtd) + (Add-on * Qtd) - Rake

Rake = Configurável por:
- Tipo: FIXO, PERCENTUAL, MISTO
- Aplicável em: buy-in, rebuy, add-on separadamente
```

### Reconciliação

```
Esperado = (Num_Entries * Buyin) + (Rebuy_Usado * Rebuy_Valor)
Realizado = SUM(premiacao_recebida) + Rake_Calculado

Discrepância = |Esperado - Realizado|
```

---

## 7. APIs Disponíveis

### Endpoints de Dados

```
GET /api/ranking/<season_id>/          → JSON com ranking
GET /api/player/<player_id>/stats/     → Estatísticas do jogador
GET /api/tournament/<tournament_id>/   → Detalhes do torneio
POST /api/financial/reconcile/         → Reconciliar caixa
```

### Exemplo de Resposta

```json
{
  "success": true,
  "data": {
    "ranking": [
      {
        "posicao": 1,
        "jogador": "João Silva",
        "pontos": 450,
        "participacoes": 8,
        "vitoria": 3
      }
    ]
  }
}
```

---

## 8. Performance e Otimizações

### Queries Otimizadas

```python
# ❌ RUIM - N+1 queries
players = Player.objects.all()
for player in players:
    print(player.season)  # Query por jogador!

# ✅ BOM - Select related
players = Player.objects.select_related('season')
for player in players:
    print(player.season)  # Sem queries adicionais
```

### Caching Estratégico

```python
# Cache ranking (atualiza só ao terminar torneio)
cache.set('ranking_season_1', ranking_data, timeout=3600)

# Cache estatísticas do jogador
cache.set(f'player_stats_{player_id}', stats, timeout=600)
```

### Índices no Banco

```sql
CREATE INDEX idx_tournament_entry_player ON tournament_entry(player_id);
CREATE INDEX idx_tournament_result_player ON tournament_result(player_id);
CREATE INDEX idx_playerstatistics_season ON playerstatistics(season_id);
```

---

## 9. Segurança

### Proteção contra Vulnerabilidades

| Vulnerabilidade | Proteção |
|-----------------|----------|
| SQL Injection | ORM Django (parameterized queries) |
| XSS | Template escaping automático |
| CSRF | @csrf_protect + CSRF tokens em forms |
| Acesso não autorizado | @login_required + @tenant_required |
| Dados expostos | Isolamento multi-tenant |

### Checklist de Segurança

- [ ] DEBUG = False em produção
- [ ] SECRET_KEY forte e aleatória
- [ ] HTTPS obrigatório (SECURE_SSL_REDIRECT = True)
- [ ] SECURE_HSTS_SECONDS configurado
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Senhas hasheadas com PBKDF2

---

## 10. Deployment

### Requisitos de Produção

```
Python 3.10+
PostgreSQL 12+
Nginx (reverse proxy)
Gunicorn (WSGI server)
Redis (cache opcional)
Supervisor (process manager)
```

### Checklist de Deploy

```bash
1. Clonar repositório
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py collectstatic
5. python manage.py check --deploy
6. Configurar variáveis de ambiente (.env)
7. Iniciar Gunicorn com Supervisor
8. Configurar Nginx como reverse proxy
9. Testar HTTPS
10. Monitorar logs
```

### Arquivo .env Exemplo

```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/pokerclube
ALLOWED_HOSTS=pokerclube.com,www.pokerclube.com
SECURE_SSL_REDIRECT=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

---

## 11. Extensões Futuras

### API REST Completa
```python
# Usar Django REST Framework
class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
```

### Notificações em Tempo Real
```python
# Usar Django Channels
@database_sync_to_async
def new_tournament_created(event):
    # Notificar jogadores via WebSocket
    await channel_layer.group_send(
        f"tournament_{tournament_id}",
        {"type": "tournament.notification", ...}
    )
```

### Mobile App
```
React Native / Flutter
Conecta a API REST existente
Sincronização offline
Push notifications
```

---

## 12. Troubleshooting

### Problema: "Tenant não configurado"
**Causa**: User não tem TenantUser
**Solução**: 
```python
TenantUser.objects.create(user=user, tenant=tenant, role='player')
```

### Problema: Ranking não atualiza
**Causa**: Função _calcular_e_atualizar_stats não foi chamada
**Solução**: Chamar após criar TournamentResult
```python
from core.views.ranking import _calcular_e_atualizar_stats
_calcular_e_atualizar_stats(tournament.season, player, tenant)
```

### Problema: Dados lentos
**Causa**: Queries não otimizadas ou cache não configurado
**Solução**: Usar select_related/prefetch_related e Redis

---

## 📚 Referências

- Django Docs: https://docs.djangoproject.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Bootstrap Docs: https://getbootstrap.com/docs/
- Git Guide: https://git-scm.com/doc

---

**Última atualização**: 16 de Dezembro de 2025
**Versão do Sistema**: 1.0.0
