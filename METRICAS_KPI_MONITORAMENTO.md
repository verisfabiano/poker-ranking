# 📈 MÉTRICAS DE SAÚDE DO SISTEMA & KPIs

## Dashboard de Monitoramento

---

## 🎯 KPIs de Negócio

### 1. Métrica de Adoção
```
Jogadores por Clube:
├─ Total de jogadores cadastrados
├─ Jogadores ativos (participaram de torneio no último mês)
├─ Taxa de retenção (% que voltam no mês seguinte)
└─ Churn rate (% que saem)

Meta Inicial:
├─ 100-200 jogadores por clube
├─ 70%+ engagement mensal
├─ <10% churn rate
```

### 2. Métrica Financeira
```
Receita por Clube:
├─ Rake total (valor fixo que fica com o clube)
├─ Rake médio por torneio
├─ Receita por jogador (ARPU)
├─ Faturamento mensal total

Meta Inicial:
├─ R$500-1000/mês por clube
├─ 5-10% de rake (padrão do mercado)
├─ Crescimento 20% mês a mês
```

### 3. Métrica de Engagement
```
Participação em Torneios:
├─ Média de jogadores por torneio
├─ Taxa de presença (inscrito vs compareceu)
├─ Rebuys por jogador (média)
├─ Add-ons por jogador (média)

Meta Inicial:
├─ 30-50 jogadores por torneio
├─ 80%+ presença (confirmado vs compareceu)
├─ 0.5+ rebuys por jogador
├─ 0.3+ add-ons por jogador
```

---

## 🔧 KPIs Técnicos

### 1. Performance
```
Métricas de Velocidade:
├─ Page Load Time (PgLT)
│  └─ Meta: < 2 segundos (P95)
├─ First Contentful Paint (FCP)
│  └─ Meta: < 1 segundo
├─ Largest Contentful Paint (LCP)
│  └─ Meta: < 2.5 segundos
├─ Time to Interactive (TTI)
│  └─ Meta: < 3 segundos
└─ Cumulative Layout Shift (CLS)
   └─ Meta: < 0.1

Como medir:
- Google PageSpeed Insights
- Lighthouse CI
- New Relic APM
```

### 2. Confiabilidade
```
Métricas de Uptime:
├─ Availability (% tempo online)
│  └─ Meta: 99.9% (30min downtime/mês)
├─ MTTR (Mean Time To Recovery)
│  └─ Meta: < 15 minutos
├─ MTBF (Mean Time Between Failures)
│  └─ Meta: > 7 dias
└─ Error Rate
   └─ Meta: < 0.1% (1 erro por 1000 requests)

Como medir:
- Sentry.io (error tracking)
- UptimeRobot.com (monitoring)
- New Relic (APM)
```

### 3. Segurança
```
Métricas de Segurança:
├─ SSL/TLS Grade
│  └─ Meta: A+ (via ssllabs.com)
├─ Security Headers
│  └─ Meta: Grade A (via securityheaders.com)
├─ OWASP Top 10
│  └─ Meta: 0 vulnerabilidades críticas
├─ Penetration Test Results
│  └─ Meta: 0 críticos, <5 médios
└─ Audit Log Completeness
   └─ Meta: 100% de transações registradas

Como medir:
- SSL Labs
- Security Headers
- OWASP ZAP
- Burp Suite
```

### 4. Banco de Dados
```
Métricas DB:
├─ Query Performance
│  └─ P95 query time: < 200ms
│  └─ P99 query time: < 500ms
├─ Database Size
│  └─ Monitorar crescimento
│  └─ Backup size
├─ Connection Pool
│  └─ Max connections: 20
│  └─ Active connections: < 10
├─ Replication Lag
│  └─ Meta: < 1 segundo
└─ Backup Success Rate
   └─ Meta: 100% (0 falhas)

Como medir:
- Railway Dashboard
- pg_stat_statements
- New Relic Database Monitoring
```

---

## 📊 Relatório Semanal de Saúde

### Template para Monitorar
```markdown
# WEEKLY HEALTH REPORT - Semana XX

## Uptime & Availability
- Uptime: 99.8% (1 down de 5min)
- Erros 5xx: 0
- Erros 4xx: <5

## Performance
- Page Load: 1.2s (↓ 0.1s)
- Database: 45ms (→)
- API Response: 120ms (→)

## Tráfego
- Pageviews: 5,234 (↑ 10%)
- Unique Users: 324 (↑ 5%)
- Sessions: 789 (↑ 8%)

## Segurança
- Failed Logins: 23 (bloqueados por rate limit)
- SQL Injection Attempts: 0
- XSS Attempts: 0

## Negócio
- Novos Jogadores: 12
- Novos Torneios: 5
- Rake Coletado: R$1,234.56
- Engagement Rate: 72%

## Problemas/Alerts
- [ ] Cache hit rate baixo (45%)
- [ ] Database connection pool em 18/20

## Actions
- [ ] Aumentar cache TTL
- [ ] Investigar N+1 queries
```

---

## 🚨 Alertas Críticos

### Setup de Alertas no Sentry + NewRelic
```python
# settings.py - Sentry Configuration
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    
    # Alertas de performance
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    
    # Alertas de erro
    before_send=lambda event, hint: event,
)

# Alertar se:
# - 5xx errors > 5 por hora
# - Page load > 5 segundos (P95)
# - Database query > 1 segundo
# - Error rate > 1%
# - Uptime < 99%
```

### Slack Notifications
```python
# core/notifications.py
import requests

def notify_slack_critical(message):
    """Notificar erro crítico no Slack"""
    webhook = os.getenv('SLACK_WEBHOOK')
    payload = {
        'text': f'🚨 ALERTA CRÍTICO\n{message}',
        'channel': '#alerts',
        'username': 'PokerRanking Bot',
        'icon_emoji': ':warning:'
    }
    requests.post(webhook, json=payload)

# Usar em:
# - Transação financeira acima de R$10k
# - Error rate acima de 1%
# - Downtime detectado
# - Rate limiting ativado
```

---

## 📐 Dashboard com Grafana

### Setup Básico (Recomendado)
```yaml
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

### Métricas para Monitorar (via prometheus_client)
```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Contadores
login_attempts = Counter('login_attempts_total', 'Total login attempts')
login_failures = Counter('login_failures_total', 'Failed login attempts')
tournaments_created = Counter('tournaments_created_total', 'Total tournaments')
results_registered = Counter('results_registered_total', 'Results registered')

# Histogramas (distribuição)
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration'
)
query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration'
)

# Gauges (estado atual)
active_users = Gauge('active_users', 'Currently active users')
database_connections = Gauge('db_connections', 'Active DB connections')
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate percentage')

# Usar em views
from core.metrics import login_attempts, active_users

@app.route('/login', methods=['POST'])
def login():
    login_attempts.inc()
    # ... resto do código
```

---

## 📱 Mobile App Metrics (Futuro)

```
Se implementar app mobile:
├─ Crash Rate: < 0.1%
├─ ANR (App Not Responding): < 0.01%
├─ Hang Rate: < 0.05%
├─ Battery Impact: < 5%
├─ Data Usage: < 10MB/mês
└─ Session Length: > 5 minutos
```

---

## 💰 Análise de Custo

### Custo por Métrica Importante
```
Customer Acquisition Cost (CAC):
├─ Meta: < R$500 por cliente
├─ Benchmark: R$200-1000

Lifetime Value (LTV):
├─ Meta: > R$5000
├─ Benchmark: R$3000-10000

LTV/CAC Ratio:
├─ Meta: > 3:1
├─ Benchmark: 3:1 é break-even

Unit Economics:
├─ Rake médio por mês: R$500-1000
├─ Churn rate: <10%
├─ Payback period: 2-3 meses
```

### Infraestrutura
```
Railway.app (Atual):
├─ PostgreSQL: R$37/mês (pro)
├─ App Server: R$7-50/mês (variável)
├─ Total: ~R$50-100/mês

Crescimento (100 clubes):
├─ Database: R$300-500/mês
├─ Servers: R$1000-2000/mês
├─ CDN/Cache: R$200-300/mês
├─ Monitoring: R$100-200/mês
└─ Total: ~R$1600-3000/mês

Revenue:
├─ 100 clubes x R$50/mês (plano básico)
├─ = R$5000/mês
├─ Margem: 60-70%
└─ Lucrativo! ✅
```

---

## 🎯 Benchmark vs Concorrentes

### Comparação com Poker Trackers Conhecidos
```
PokerTracker (https://www.pokertracker4.com/)
├─ Price: $100 USD one-time
├─ Mobile: Não
├─ Cloud: Não
├─ Multi-user: Não
├─ Brasil: <10% market

Holdem Manager (https://www.holdemmanager.com/)
├─ Price: $149 USD one-time
├─ Mobile: Sim
├─ Cloud: Sim
├─ Multi-user: Não
├─ Brasil: <10% market

PokerRanking (NOSSO PRODUTO):
├─ Price: R$50/mês (SaaS)
├─ Mobile: Sim (web responsive)
├─ Cloud: Sim
├─ Multi-user: Sim (multi-tenant)
├─ Brasil: Mercado não explorado
└─ Vantagem: 💪 Multi-tenant é ÚNICO no mercado
```

---

## 📋 Checklist de Monitoramento

```markdown
## Diariamente
- [ ] Verificar uptime (UptimeRobot)
- [ ] Verificar erros críticos (Sentry)
- [ ] Verificar performance (New Relic)
- [ ] Verificar backups (Railway)

## Semanalmente
- [ ] Gerar relatório de saúde
- [ ] Revisar métricas de negócio
- [ ] Analisar churn rate
- [ ] Revisar security alerts

## Mensalmente
- [ ] Gerar relatório executivo
- [ ] Revisar roadmap vs KPIs
- [ ] Fazer penetration test
- [ ] Otimizar queries lentas

## Trimestralmente
- [ ] Auditoria de segurança
- [ ] Review de arquitetura
- [ ] Disaster recovery test
- [ ] Planejamento trimestral
```

---

## 🔗 Ferramentas Recomendadas

### Monitoramento & Alertas
- **Sentry.io** - Error tracking (grátis até 10k events/mês)
- **New Relic** - APM e performance (grátis básico)
- **UptimeRobot** - Uptime monitoring (grátis)
- **Datadog** - Observabilidade completa (pago)

### Analytics
- **Google Analytics 4** - Web analytics (grátis)
- **Mixpanel** - Event tracking (grátis até 100k eventos)
- **Amplitude** - User behavior (grátis básico)

### Security
- **OWASP ZAP** - Vulnerability scanner (grátis)
- **Burp Suite Community** - Penetration testing (grátis)
- **SSL Labs** - SSL/TLS testing (grátis)

### Performance
- **Google PageSpeed** - Page performance (grátis)
- **GTmetrix** - Detailed metrics (grátis)
- **WebPageTest** - Advanced testing (grátis)

---

## 📞 Contatos para Escalação

```
Problema             | Contato           | SLA
─────────────────────|───────────────────|──────────
Downtime total       | CTO / DevOps      | 15min
Erro crítico         | Dev Lead          | 1h
Performance lenta    | Backend Lead      | 4h
Segurança            | Security Team     | 2h
Dados inconsistentes | Database Admin    | 30min
```

---

**Última atualização:** 26 de janeiro de 2026

