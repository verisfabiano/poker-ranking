# Documentação do Sistema de Relatórios

## Visão Geral

O PokerRanking possui um sistema completo de geração, visualização e exportação de relatórios. O sistema suporta três tipos de relatórios:

1. **Relatórios Financeiros** - Análise completa de receita, gastos e lucratividade
2. **Relatórios de Desempenho** - Estatísticas individuais de cada jogador
3. **Relatórios de Ranking** - Snapshot do ranking em um período específico

## Arquitetura

### Estrutura de Arquivos

```
core/
├── models.py                           # Modelos Report, ReportFinanceiro, ReportDesempenho, ReportRanking
├── views/
│   └── relatorios.py                  # 9 views para CRUD e exportação de relatórios
├── services/
│   └── relatorio_service.py           # RelatorioService - lógica de geração
├── urls/
│   ├── __init__.py                    # URLs principais
│   └── relatorios.py                  # URLs para relatórios
├── templates/relatorios/
│   ├── home.html                      # Dashboard de relatórios
│   ├── listar.html                    # Lista filtrada com paginação
│   ├── detalhe.html                   # Visualização detalhada
│   ├── gerar_financeiro.html          # Formulário de geração financeira
│   ├── gerar_desempenho.html          # Formulário de geração de desempenho
│   ├── gerar_ranking.html             # Formulário de geração de ranking
│   └── confirmar_deletar.html         # Confirmação de deleção
├── migrations/
│   └── 0030_*.py                      # Migrations dos modelos de Report
```

## Modelos de Banco de Dados

### Model: Report

Campo principal que armazena metadados de qualquer tipo de relatório.

```python
class Report(models.Model):
    TIPO_CHOICES = [
        ('FINANCEIRO', 'Relatório Financeiro'),
        ('DESEMPENHO_JOGADOR', 'Desempenho do Jogador'),
        ('RANKING', 'Ranking Snapshot'),
    ]
    
    tenant = ForeignKey(Tenant)              # Multi-tenancy
    tipo = CharField(choices=TIPO_CHOICES)   # Tipo de relatório
    titulo = CharField(max_length=200)       # Título personalizado
    periodo = CharField()                    # Nome do período (ex: "Janeiro 2025")
    data_inicio = DateField()
    data_fim = DateField()
    dados = JSONField()                      # Dados genéricos (flexível)
    gerado_por = ForeignKey(User)            # Quem gerou
    criado_em = DateTimeField(auto_now_add=True)
    
    # Índices para performance
    Index(fields=['tenant', 'tipo', '-criado_em'])
    Index(fields=['tenant', 'data_inicio', 'data_fim'])
```

### Model: ReportFinanceiro (OneToOne → Report)

Métricas financeiras detalhadas.

```python
class ReportFinanceiro(models.Model):
    report = OneToOneField(Report, on_delete=CASCADE)
    
    # Faturamento
    total_buy_in = DecimalField()
    total_rebuy = DecimalField()
    total_addon = DecimalField()
    total_faturamento = DecimalField()      # buy_in + rebuy + addon
    
    # Gastos
    total_premiacao = DecimalField()
    total_rake = DecimalField()             # faturamento - premiacao
    
    # Métricas
    margem_bruta = DecimalField()           # (rake/faturamento)*100
    numero_torneios = IntegerField()
    numero_jogadores_unicos = IntegerField()
    ticket_medio = DecimalField()           # faturamento/numero_torneios
    
    # Breakdown
    lucro_liquido = DecimalField()
    detalhes_por_tipo = JSONField()         # {tipo_torneio: {buy_in, rebuy, ...}}
```

### Model: ReportDesempenho (OneToOne → Report, FK → Player, FK → Season)

Estatísticas de um jogador em uma temporada.

```python
class ReportDesempenho(models.Model):
    report = OneToOneField(Report)
    player = ForeignKey(Player)
    season = ForeignKey(Season)
    
    # Participações
    total_participacoes = IntegerField()
    total_vitórias = IntegerField()
    total_top3 = IntegerField()
    total_pontos = IntegerField()
    
    # Financeiro
    total_investido = DecimalField()        # Total buy-in do jogador
    total_ganho = DecimalField()            # Total ganho em premações
    roi = DecimalField()                    # (ganho-investido)/investido * 100
    
    # Análise Posicional
    melhor_posicao = IntegerField()
    pior_posicao = IntegerField()
    posicao_media = DecimalField()
    
    # Série Temporal
    evolucao_pontos = JSONField()           # {data: pontos, ...}
    lucro_por_dia = JSONField()             # {data: lucro_diario, ...}
```

### Model: ReportRanking (OneToOne → Report, FK → Season)

Snapshot do ranking em um momento específico.

```python
class ReportRanking(models.Model):
    report = OneToOneField(Report)
    season = ForeignKey(Season)
    
    # Jogadores Top 10
    top_10 = JSONField()                    # [
                                            #   {posicao, nome, apelido, pontos, vitórias, participacoes},
                                            #   ...
                                            # ]
    
    # Estatísticas
    total_jogadores = IntegerField()
    total_pontos_distribuidos = IntegerField()
    pontos_medio_por_jogador = DecimalField()
    
    # Tendências
    maiores_subidas = JSONField()           # Jogadores que subiram
    maiores_quedas = JSONField()            # Jogadores que caíram
```

## Service Layer

### RelatorioService

Classe centralizada para geração de relatórios. Localizada em `core/services/relatorio_service.py`.

```python
class RelatorioService:
    def __init__(self, tenant, usuario):
        self.tenant = tenant
        self.usuario = usuario
    
    def gerar_relatorio_financeiro(self, data_inicio, data_fim, titulo=None):
        """
        Gera relatório financeiro consolidado.
        
        Retorna:
            Report object com ReportFinanceiro relacionado
        """
    
    def gerar_relatorio_desempenho(self, player, season, data_inicio, data_fim, titulo=None):
        """
        Gera relatório de desempenho individual.
        
        Retorna:
            Report object com ReportDesempenho relacionado
        """
    
    def gerar_relatorio_ranking(self, season, data_inicio, data_fim, titulo=None):
        """
        Gera snapshot do ranking.
        
        Retorna:
            Report object com ReportRanking relacionado
        """
    
    def listar_relatorios(self, tipo=None, limite=20):
        """Lista relatórios com filtros opcionais"""
    
    def deletar_relatorio(self, report_id):
        """Deleta um relatório e seus dados relacionados"""
```

## Views e Endpoints

### URLs Disponíveis

| Método | URL | Nome | Descrição |
|--------|-----|------|-----------|
| GET | `/relatorios/` | `relatorios_home` | Dashboard inicial |
| GET | `/relatorios/listar/` | `relatorios_listar` | Lista todos com filtros |
| GET | `/relatorios/<id>/` | `relatorio_detalhe` | Visualiza relatório |
| GET | `/relatorios/<id>/json/` | `relatorio_json` | JSON para gráficos |
| GET | `/relatorios/<id>/exportar-csv/` | `exportar_relatorio_csv` | Exporta como CSV |
| POST | `/relatorios/<id>/deletar/` | `deletar_relatorio` | Deleta relatório |
| GET/POST | `/relatorios/gerar/financeiro/` | `gerar_relatorio_financeiro` | Gera relatório financeiro |
| GET/POST | `/relatorios/gerar/desempenho/` | `gerar_relatorio_desempenho` | Gera relatório de desempenho |
| GET/POST | `/relatorios/gerar/ranking/` | `gerar_relatorio_ranking` | Gera ranking snapshot |

### Permissões

- **Visualização**: `@login_required` + `@tenant_required` (todos os usuários autenticados)
- **Geração**: Admin-only (verificado em `tenant_user.role == 'admin'`)
- **Deleção**: Admin-only
- **Multi-tenant**: Todos os relatórios filtrados por `request.tenant`

## Templates

### home.html
Dashboard com:
- Cards de estatísticas (total de relatórios, contagem por tipo)
- Últimos 10 relatórios em tabela
- Botões de ação rápida para gerar novos relatórios
- Responsivo (3 breakpoints mobile)

### listar.html
Lista paginada com:
- Filtros por tipo de relatório
- Ordenação (mais recente, mais antigo, título)
- Ações (visualizar, exportar CSV, deletar)
- Modals de confirmação de deleção
- Estado vazio com CTA

### detalhe.html
Visualização completa com:
- **Relatório Financeiro**: Tabelas de faturamento, rake, margem, breakdown por tipo
- **Relatório de Desempenho**: Cards de estatísticas, tabela de evolução
- **Relatório de Ranking**: Top 10 com medals, estatísticas gerais
- Botões de exportação (CSV, JSON)
- Botão de voltar e data da geração

### gerar_financeiro.html
Formulário com:
- Seleção de período (data_inicio, data_fim)
- Campo de título personalizado (opcional)
- Info box explicando o que será incluído
- Defaults (últimos 30 dias)

### gerar_desempenho.html
Formulário com:
- Dropdown de jogadores
- Dropdown de temporadas
- Seleção de período (opcional, dentro da temporada)
- Campo de título personalizado

### gerar_ranking.html
Formulário com:
- Dropdown de temporadas
- Seleção de período (opcional)
- Checkboxes para opções (tendências, comparação)
- Campo de título personalizado

### confirmar_deletar.html
Confirmação com:
- Informações do relatório a deletar (tipo, período, data de criação)
- Warnings e explicações sobre irreversibilidade
- Checkbox de confirmação obrigatória
- Botões de confirmar/cancelar

## Fluxos de Uso

### Gerar Relatório Financeiro

1. Admin clica em "Nova Relatório" → "Financeiro"
2. Preenche período (ou usa default de 30 dias)
3. Clica "Gerar Relatório"
4. View `gerar_relatorio_financeiro` recebe POST
5. `RelatorioService.gerar_relatorio_financeiro()` é chamado
6. Service queries todos os Tournament da data range
7. Calcula todas as métricas agregadas
8. Cria `Report` + `ReportFinanceiro`
9. Redireciona para `relatorio_detalhe`
10. Admin vê a visualização completa

### Exportar para CSV

1. Admin está visualizando relatório
2. Clica em botão "CSV"
3. View `exportar_relatorio_csv` gera arquivo
4. Write rows com dados estruturados
5. Browser faz download de `relatorio_<id>.csv`

### Deletar Relatório

1. Admin em `relatorios_listar` clica ícone lixeira
2. Modal de confirmação aparece
3. Admin clica "Deletar Permanentemente"
4. Redireciona para `confirmar_deletar.html`
5. Admin marca checkbox de confirmação
6. Clica "Deletar Permanentemente"
7. View `deletar_relatorio` deleta Report + relacionados (cascade)
8. Redireciona para `relatorios_listar`

## Segurança e Validação

### Multi-tenancy
```python
# Todo acesso filtrado por tenant
relatorios = Report.objects.filter(tenant=request.tenant)
```

### Permissões
```python
# Admin-only para geração/deleção
tenant_user = request.user.tenant_users.filter(tenant=request.tenant).first()
if tenant_user and tenant_user.role != 'admin':
    return render(request, 'erro.html', {'mensagem': 'Permissão negada'}, status=403)
```

### Validação
```python
# Validar ordem de datas
if data_inicio > data_fim:
    return render(request, '...', {'erro': 'Data de início não pode ser posterior...'})

# Validar existência de objetos
player = get_object_or_404(Player, id=player_id, tenant=request.tenant)
```

## Performance

### Índices
- `(tenant, tipo, -criado_em)` - Acelera listagem filtrada
- `(tenant, data_inicio, data_fim)` - Acelera queries por período

### Otimizações ORM
- `select_related()` para ForeignKeys
- `prefetch_related()` para RelatedManagers
- JSONField para dados heterogêneos (evita N+1)

### Cachabilidade
- JSONField é estático após geração
- Relatórios não mudam (immutable)
- Perfeito para cache de leitura

## Próximas Melhorias

### Phase 1 (Próximas)
- [ ] Integração com Chart.js para gráficos
- [ ] Exportação para PDF
- [ ] Filtros avançados (por jogador, tipo de torneio)
- [ ] Comparação de períodos

### Phase 2 (Futuro)
- [ ] Geração automática via Celery
- [ ] Agendamento de relatórios
- [ ] Envio por email
- [ ] API REST completa
- [ ] Dashboards em tempo real

### Phase 3 (Longo prazo)
- [ ] Data warehouse para BigData
- [ ] ML para previsões
- [ ] Alertas inteligentes
- [ ] Integração com BI tools (Tableau, PowerBI)

## Exemplos de Uso

### Gerar Relatório via Shell Django

```python
from core.services.relatorio_service import RelatorioService
from core.models import Tenant, Season, Player
from datetime import date, timedelta

tenant = Tenant.objects.first()
user = tenant.admin_user
service = RelatorioService(tenant, user)

# Financeiro
report = service.gerar_relatorio_financeiro(
    data_inicio=date(2025, 1, 1),
    data_fim=date(2025, 1, 31),
    titulo="Financeiro - Janeiro 2025"
)

# Desempenho
player = Player.objects.first()
season = Season.objects.first()
report = service.gerar_relatorio_desempenho(
    player=player,
    season=season,
    data_inicio=date(2025, 1, 1),
    data_fim=date(2025, 1, 31)
)

# Ranking
report = service.gerar_relatorio_ranking(
    season=season,
    data_inicio=date(2025, 1, 1),
    data_fim=date(2025, 1, 31)
)
```

### Acessar Relatórios em Jinja2

```html
<!-- Template -->
{% for report in relatorios %}
    <h3>{{ report.titulo }}</h3>
    <p>{{ report.data_inicio|date:"d/m/Y" }} - {{ report.data_fim|date:"d/m/Y" }}</p>
    
    {% if report.tipo == 'FINANCEIRO' %}
        <p>Faturamento: R$ {{ report.financeiro.total_faturamento }}</p>
    {% endif %}
{% endfor %}
```

## Troubleshooting

### Relatório não aparece em listar?
1. Verificar se é admin (permissão)
2. Verificar se está no mesmo tenant
3. Checker em core_report na database

### Erro ao gerar relatório?
1. Validar período (data_inicio < data_fim)
2. Validar se player/season existem no tenant
3. Checker logs: `python manage.py shell`

### CSV vazio ou mal formatado?
1. Verificar tipo de relatório
2. Verificar dados no JSONField
3. Adicionar campos em `exportar_relatorio_csv`

---

**Última atualização**: 30 de dezembro de 2025  
**Versão**: 1.0  
**Status**: Funcional e em produção
