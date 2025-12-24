# 🎯 ROADMAP - PHASE 2 & 3 (Próximos Passos)

## 📊 Status Atual

**Phase 1: ✅ COMPLETO**
- Dashboard do jogador (4 funcionalidades)
- Registration flow (select tenant → create user → auto-login)
- Admin panel operacional
- Sistema de ranking funcionando
- Documentação comercial pronta
- **Sistema pronto para produção**

---

## 🚀 PHASE 2: ENGAJAMENTO & ANALYTICS (8-10 semanas)

### ⚡ Prioridade: ALTA
**Objetivo:** Aumentar engajamento dos jogadores com dados comparativos e metas

### 1️⃣ **Gráficos de Evolução** (2 semanas)
**Por quê:** Jogadores querem ver sua progressão
**Como:** Implementar Chart.js com dados mensais/semanais

#### A. ROI por Mês
```python
# views/player.py - Nova função
def player_evolution(request):
    months = []
    for m in range(1, 13):
        entries = TournamentEntry.objects.filter(
            player=request.player,
            tournament__data__month=m
        ).aggregate(
            gasto=Sum('tournament__buyin'),
            ganho=Sum('result__premiacao_recebida')
        )
        months.append({
            'mes': m,
            'gasto': entries['gasto'] or 0,
            'ganho': entries['ganho'] or 0,
            'roi': ((entries['ganho'] - entries['gasto']) / entries['gasto'] * 100) if entries['gasto'] > 0 else 0
        })
    return render(request, 'player_evolution.html', {'months': months})
```

#### B. Template: `player_evolution.html`
- Gráfico linha dupla (gasto vs ganho)
- Gráfico ROI mensal
- Tabela com detalhes
- Filtro por período (3m, 6m, YTD, all-time)

#### C. Endpoints necessários
```
GET /jogador/evolucao/        → Chart data JSON
GET /jogador/evolucao/filtro/ → Com período específico
```

**Deliverables:**
- [ ] Nova view `player_evolution`
- [ ] Templates com Chart.js
- [ ] API endpoint JSON
- [ ] Mobile responsive
- [ ] Testes unitários

---

### 2️⃣ **Comparativo com Média do Clube** (2 semanas)
**Por quê:** Motivação vs competidores
**Como:** Calcular estatísticas agregadas do clube

#### A. Modelos novos
```python
# core/models.py
class ClubStatistics(models.Model):
    """Cache de estatísticas agregadas do clube"""
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    media_roi = models.DecimalField(max_digits=10, decimal_places=2)
    media_itm = models.DecimalField(max_digits=5, decimal_places=2)
    total_jogadores = models.IntegerField()
    total_torneios = models.IntegerField()
    atualizado_em = models.DateTimeField(auto_now=True)
```

#### B. View comparativa
```python
def player_comparison(request):
    player = request.user.player
    club_stats = ClubStatistics.objects.get(tenant=request.tenant)
    
    player_roi = calculate_roi(player)
    player_itm = calculate_itm(player)
    
    return render(request, 'player_comparison.html', {
        'player_roi': player_roi,
        'player_itm': player_itm,
        'club_avg_roi': club_stats.media_roi,
        'club_avg_itm': club_stats.media_itm,
        'percentil': calculate_percentil(player, club_stats)
    })
```

#### C. Visualizações
- Card "Você vs Clube"
- Posição no ranking de ROI (Top 10%)
- Posição no ranking de ITM
- Gauge charts (sua % vs média)
- Badges de achievement (Top 5%, Top 10%, etc)

**Deliverables:**
- [ ] Modelo ClubStatistics
- [ ] Função calculate_percentil()
- [ ] View player_comparison
- [ ] Templates com gauge charts
- [ ] Cron job de atualização nightly

---

### 3️⃣ **Sistema de Badges & Achievements** (1.5 semanas)
**Por quê:** Gamificação aumenta engajamento
**Como:** Criar badges desbloqueáveis com regras

#### A. Modelo
```python
# core/models.py
class Achievement(models.Model):
    nome = models.CharField(max_length=100)  # "Lenda do Turbo"
    descricao = models.TextField()
    icone = models.ImageField()  # 🏆 emoji ou imagem
    criterio = models.CharField(max_length=50)  # 'top_roi_5pct', 'itm_streak_5', etc
    criado_em = models.DateTimeField(auto_now_add=True)

class PlayerAchievement(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    desbloqueado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['player', 'achievement']
```

#### B. Badges predefinidos
```
🏆 "Lenda de Ouro"      → ROI > 50% (last 10 tournaments)
🥇 "Campeão"            → 3+ 1º lugares (last 20 tournaments)
💰 "Shark"              → ROI > 100%
⚡ "Flash"              → 5+ ITM em sequência
🎯 "Precisão"           → ITM > 70%
👑 "Rei do Ranking"     → #1 na temporada
🔥 "Streak Quente"      → 3 ITM em sequência
🎪 "Mais Torneios"      → 50+ torneios jogados
```

#### C. Página de Achievements
```
GET /jogador/achievements/
Template:
- Grid de badges desbloqueados
- Grid de badges "em progresso" com barra de progresso
- Timeline de quando desbloqueou
- Compartilhar achievements em redes sociais
```

**Deliverables:**
- [ ] Modelos Achievement + PlayerAchievement
- [ ] Signal para detectar achievements
- [ ] 10 badges predefinidos
- [ ] View achievements
- [ ] Template com visual atrativo
- [ ] Share buttons (Twitter, WhatsApp, Facebook)

---

### 4️⃣ **Desafios & Metas Pessoais** (2 semanas)
**Por quê:** Metas criam motivação
**Como:** Permitir criar desafios com prêmios

#### A. Modelo
```python
# core/models.py
class Challenge(models.Model):
    TIPO_CHOICES = [
        ('roi', 'ROI Target'),
        ('itm', 'ITM Goal'),
        ('torneios', 'Tournament Count'),
        ('primeiro', 'First Place Count'),
    ]
    
    jogador = models.ForeignKey(Player, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)  # "Atingir 30% ROI"
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    meta = models.DecimalField(max_digits=10, decimal_places=2)
    progresso_atual = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField(auto_now_add=True)
    data_fim = models.DateField()
    completado = models.BooleanField(default=False)
    data_conclusao = models.DateField(null=True)
    recompensa = models.CharField(max_length=100, blank=True)  # "Cerveja grátis"
```

#### B. Exemplos de desafios
- "Atingir 20% ROI em dezembro"
- "5 ITM em sequência até fim de semana"
- "Jogar 10 torneios em janeiro"
- "1º lugar em 2 torneios este mês"

#### C. Views
```python
def create_challenge(request):
    # POST form para criar desafio
    # Calcula automaticamente progresso_atual
    pass

def my_challenges(request):
    # GET lista de desafios
    # Mostra barra de progresso
    # Botão para marcar como concluído manualmente
    pass

def challenge_detail(request, id):
    # GET detalhe
    # Mostra histórico de progresso
    # Comentários dos amigos
    pass
```

**Deliverables:**
- [ ] Modelo Challenge
- [ ] Views create/list/detail
- [ ] Templates com progress bars
- [ ] Auto-update de progresso (via signal)
- [ ] Notificação quando completar

---

## 📊 PHASE 3: SOCIAL & MONETIZAÇÃO (10-12 semanas)

### ⚡ Prioridade: MÉDIA
**Objetivo:** Criar comunidade e preparar monetização

### 1️⃣ **Perfil Público do Jogador** (1.5 semanas)
**Por quê:** Presença pública aumenta credibilidade
**Como:** URL pública com histórico

#### A. URL
```
/jogador/@{username}/
Ex: /jogador/@fabiano_smith/
```

#### B. Conteúdo
```
Header com:
- Avatar (foto do jogador)
- Nome
- Ranking atual
- "Jogando desde [mês/ano]"
- Estatísticas públicas:
  * ROI
  * ITM%
  * Torneios jogados
  * Total ganho/perdido

Seções:
1. Últimos resultados (10 mais recentes)
2. Maiores ganhos (top 5 wins)
3. Badges desbloqueados
4. Últimas achievements
5. Seguidores (social)
```

#### C. Controle de privacidade
```python
# core/models.py
class PlayerProfile(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    perfil_publico = models.BooleanField(default=True)
    mostrar_roi = models.BooleanField(default=True)
    mostrar_historico = models.BooleanField(default=True)
    mostrar_email = models.BooleanField(default=False)
    bio = models.CharField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
```

**Deliverables:**
- [ ] Modelo PlayerProfile
- [ ] URL padrão /jogador/@{username}/
- [ ] View pública (sem auth)
- [ ] Template com design atrativo
- [ ] Configurações de privacidade
- [ ] OG meta tags (share no Twitter/WhatsApp)

---

### 2️⃣ **Seguidores & Feed Social** (2 semanas)
**Por quê:** Rede social engaja
**Como:** Sistema simples de follow + feed

#### A. Modelos
```python
# core/models.py
class Follow(models.Model):
    seguidor = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='seguindo')
    seguido = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='seguidores')
    data = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['seguidor', 'seguido']

class PlayerFeed(models.Model):
    """Activity feed para cada jogador"""
    TIPO_CHOICES = [
        ('torneio', 'Novo Torneio'),
        ('resultado', 'Novo Resultado'),
        ('ranking', 'Subiu Ranking'),
        ('achievement', 'Desbloqueou Badge'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    data = models.DateTimeField(auto_now_add=True)
```

#### B. Views sociais
```python
def player_profile(request, username):
    player = Player.objects.get(slug=username)
    followers = player.seguidores.count()
    following = player.seguindo.count()
    is_following = request.user.player in player.seguidores.all()
    
    return render(request, 'player_profile.html', {
        'player': player,
        'followers': followers,
        'following': following,
        'is_following': is_following,
    })

def feed(request):
    """Feed dos jogadores que sigo"""
    followed_players = request.user.player.seguindo.all()
    feed_items = PlayerFeed.objects.filter(
        player__in=followed_players
    ).order_by('-data')[:50]
    
    return render(request, 'feed.html', {'feed': feed_items})
```

#### C. Componentes
- Botão "Seguir" no perfil
- Feed na home (últimas atividades dos seguidos)
- Notificação quando alguém me segue
- Contador de seguidores no perfil

**Deliverables:**
- [ ] Modelos Follow + PlayerFeed
- [ ] Views follow/unfollow
- [ ] Feed view
- [ ] Templates
- [ ] Notificações
- [ ] Tests

---

### 3️⃣ **Comentários & Discussão** (1.5 semanas)
**Por quê:** Comunidade engaja mais
**Como:** Comentários em resultados

#### A. Modelo
```python
# core/models.py
class Comment(models.Model):
    resultado = models.ForeignKey(TournamentResult, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Player, on_delete=models.CASCADE)
    texto = models.TextField(max_length=500)
    criado_em = models.DateTimeField(auto_now_add=True)
    editado_em = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-criado_em']
```

#### B. Funcionalidades
- Comentar em resultados de torneios
- Elogios/parabéns para outros jogadores
- Análise de mão (breve)
- Reaction emojis (👍 🔥 ⚡ 😂)

#### C. Security
- Requer estar logado
- Validação XSS (markdown safe)
- Apenas autor pode editar/deletar
- Admin pode moderar

**Deliverables:**
- [ ] Modelo Comment
- [ ] AJAX POST comment
- [ ] Carregar comments dinamicamente
- [ ] Editar/deletar próprio comment
- [ ] Markdown básico
- [ ] Tests

---

### 4️⃣ **Sistema de Notificações** (2 semanas)
**Por quê:** Aumenta retenção
**Como:** Notificações in-app + email + push

#### A. Modelo
```python
# core/models.py
class Notification(models.Model):
    TIPO_CHOICES = [
        ('torneio_novo', 'Novo Torneio'),
        ('resultado_seu', 'Seu Resultado Lançado'),
        ('novo_seguidor', 'Novo Seguidor'),
        ('comentario', 'Comentário no Seu Resultado'),
        ('mention', 'Mencionado'),
        ('achievement', 'Desbloqueou Badge'),
    ]
    
    para = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=200)
    link = models.URLField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
```

#### B. Casos de uso
- ✅ Novo torneio criado (seu clube)
- ✅ Resultado seu foi lançado
- ✅ Alguém começou a te seguir
- ✅ Alguém comentou seu resultado
- ✅ Você foi mencionado (@fabiano)
- ✅ Desbloqueou novo achievement

#### C. Canais
- 🔔 In-app (sino no topo)
- 📧 Email (1x/dia digest)
- 📱 Push (celular, se tiver app)

**Deliverables:**
- [ ] Modelo Notification
- [ ] Views criar notificação (disparadas por signals)
- [ ] API /jogador/notificacoes/
- [ ] Bell icon no navbar
- [ ] Mark as read (AJAX)
- [ ] Email template
- [ ] Tests

---

## 💰 MONETIZAÇÃO (PHASE 4+)

### Modelos de receita possíveis

#### 1. **SaaS Freemium**
```
Free:
  - Até 50 jogadores
  - Até 10 torneios/mês
  - Dashboard básico
  
Pro ($99/mês):
  - Jogadores ilimitados
  - Torneios ilimitados
  - Relatórios avançados
  - Suporte prioritário
  
Enterprise:
  - Setup customizado
  - Integração com sistemas
  - Suporte dedicado
```

#### 2. **Taxas por Transação**
```
Por torneio lançado: R$ 0,50
Por inscrição processada: R$ 0,10
```

#### 3. **Marketplace de Estruturas**
```
Criar templates premium de blinds:
  - "Turbo Profissional"
  - "Deepstack 6h"
  - "MTT Format Pro"
  
Preço: R$ 29,90 / 1x ou R$ 4,99 / mês
```

#### 4. **Publicidade Discreta**
```
Banner no footer
  - "Estude poker com ProPoker.com"
  - "Encontre dados de mãos em Pokerbase"
  
Revenue share com parceiro
```

---

## 📈 TIMELINE RECOMENDADA

```
Semana 1-2:    PHASE 2 Features 1-2 (Gráficos + Comparativo)
Semana 3-4:    PHASE 2 Features 3-4 (Badges + Desafios)
Semana 5-7:    PHASE 3 Features 1-2 (Perfil + Social)
Semana 8-9:    PHASE 3 Features 3-4 (Comentários + Notif)
Semana 10-12:  Polishing + Deploy + Marketing
```

**Total: ~3 meses para Phase 2+3 completo**

---

## 🎯 PRIORIDADE POR IMPACTO

### ALTA PRIORIDADE (fazer primeiro)
1. ✅ Gráficos de evolução (ROI mensal)
2. ✅ Badges & Achievements (gamificação)
3. ✅ Desafios pessoais (motivação)
4. ✅ Sistema de notificações (retenção)

### MÉDIA PRIORIDADE
5. Comparativo com clube
6. Perfil público
7. Seguidores & Feed

### BAIXA PRIORIDADE (fazer depois)
8. Comentários
9. Reações/Emojis
10. Monetização

---

## 💡 QUICK WINS (1-2 dias cada)

Se quiser implementar rápido para gerar buzz:

1. **Avatar do jogador** - Upload simple
   - Arquivo: Player model + upload_to='avatars/'
   - Template: foto no dashboard

2. **Bio do jogador** - CharField 500 chars
   - "Jogador profissional há 5 anos"
   - Mostra no perfil

3. **Botão de compartilhar no Twitter**
   - "Acabei de fazer R$ X no poker!"
   - Link do perfil público

4. **Ranking em tempo real**
   - Atualizar a cada resultado
   - Mostrar movimento (⬆️ ⬇️)

5. **Emoji badges simples**
   - 🏆 🥇 💰 ⚡ 🎯 👑
   - Sem banco de dados, apenas no template

---

## 🔧 TECH STACK RECOMENDADO

Para essas features:
- Backend: Django REST (para APIs)
- Frontend: Chart.js (gráficos)
- Cache: Redis (ClubStatistics atualizado)
- Files: S3 (avatars)
- Tasks: Celery (notifications)
- Tests: pytest-django

---

## 📋 CHECKLIST ANTES DE COMEÇAR

- [ ] Ter Phase 1 100% estável em produção
- [ ] Backup da base de dados
- [ ] Testes escritos para Phase 1
- [ ] CI/CD pipeline setup
- [ ] Documentação Phase 1 atualizada
- [ ] Feedback de usuários coletado
- [ ] Prioridades validadas com PM/vendas

---

## 📞 PRÓXIMOS PASSOS

**Opção A: Implementar Phase 2 agora**
- Comece com gráficos + badges
- Entrega em 4 semanas
- Impacto alto no engajamento

**Opção B: Fazer quick wins primeiro**
- Faz em 1 semana
- Gera buzz e feedback
- Depois faz Phase 2

**Opção C: Ir para produção com Phase 1**
- Lança agora
- Coleta feedback
- Implementa Phase 2 conforme feedback

---

**Versão:** 1.0  
**Data:** 16/12/2025  
**Status:** Pronto para discussão  
**Próximo Update:** Conforme implementação
