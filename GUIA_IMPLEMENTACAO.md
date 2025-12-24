# 📋 PokerClube - Guia de Implementação Rápida

## 🎯 Este Documento é Para

- **Gerentes de Clube**: Entender como será a operação
- **Desenvolvedores**: Setup rápido para começar
- **Prospects**: Ver funcionando em 5 minutos

---

## ⚡ Quick Start (5 minutos)

### Pré-requisitos
- Python 3.10+ instalado
- Git instalado
- Editor de texto (opcional)

### 1. Clonar e Setup

```bash
# Clonar repositório
git clone https://github.com/verisfabiano/poker-ranking.git
cd poker-ranking

# Criar virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python manage.py migrate

# Criar admin
python manage.py createsuperuser
  Username: admin
  Email: admin@test.com
  Senha: admin123

# Iniciar servidor
python manage.py runserver
```

### 2. Acessar Sistema

Abra no navegador: **http://127.0.0.1:8000/**

### 3. Login Inicial

- **URL**: http://127.0.0.1:8000/jogador/login/
- **Email**: admin@test.com
- **Senha**: admin123
- **Resultado**: Acesso ao dashboard admin

---

## 📊 Fluxo de Uso - Primeiro Torneio

### Passo 1: Preparação (5 min)

Admin acessa: `/painel/` → Dashboard

**Verificar:**
- ✓ Temporada 2025 existe e está ativa
- ✓ Estrutura de blinds carregada
- ✓ Tipo de torneio "Regular" configurado

**Se faltar algo:**
```
Criar Temporada:
  - Nome: "Temporada 2025"
  - Data Início: 01/01/2025
  - Ativa: SIM

Criar Tipo de Torneio:
  - Nome: "Regular"
  - Multiplicador Pontos: 1.0
  - Descrição: "Torneio padrão"
```

### Passo 2: Criar Torneio (3 min)

**Acesso**: `/temporadas/` → Selecionar Temporada → "Novo Torneio"

**Preencher:**
```
Nome: "Texas Hold'em - Sexta à Noite"
Data/Hora: 2025-12-19 20:00
Buy-in: R$ 100,00
Permite Rebuy: SIM
Valor Rebuy: R$ 100,00
Permite Add-on: SIM
Valor Add-on: R$ 50,00
Tipo: Regular
Rake: R$ 10,00 (fixo)
```

**Resultado**: Torneio agendado, jogadores podem se inscrever

### Passo 3: Inscrição de Jogadores (2 min)

**Como Jogador:**
- Acessa: `/jogador/torneios/`
- Clica "Inscrever-se" no torneio
- Confirmação imediata

**Como Admin:**
- Acessa: `/torneio/[id]/jogadores/`
- Aprova inscrições
- Pode adicionar jogadores manualmente

### Passo 4: Lançamento de Resultados (5 min)

**Acesso**: `/torneio/[id]/lancamento/`

**Preencher posições:**
```
1º lugar: João Silva (R$ 400)
2º lugar: Maria Santos (R$ 300)
3º lugar: Pedro Costa (R$ 200)
...
```

**Sistema calcula automaticamente:**
- ✓ Premiação
- ✓ Pontos do ranking
- ✓ Estatísticas do jogador
- ✓ Rake e receita

### Passo 5: Visualizar Resultados

**Dashboard do Jogador** (`/jogador/home/`):
- Novo saldo financeiro atualizado
- Ranking posição atualizada
- Últimos resultados mostrados

**Ranking Público** (`/ranking/[season_id]/`):
- Posição de cada jogador
- Pontos acumulados
- Evolução de performance

---

## 👥 Fluxo - Gerenciamento de Usuários

### Criar novo jogador como Admin

```
Admin → /jogadores/ → "Novo Jogador"

Nome: "Carlos Mendes"
Apelido: "Mendes"
Email: carlos@email.com
Status: Ativo
```

**Resultado:** Jogador pode fazer login com email/senha

### Criar novo admin/moderador

```
Django Admin → Users → Add User
  Username: moderador1
  Email: mod@email.com
  Password: ___
  Is Staff: ✓
  Is Superuser: ✗
```

**Depois vincular ao Tenant:**
```
Django Admin → Tenant Users → Add
  User: moderador1
  Tenant: ESPAÇO POKER ITAPEMA
  Role: admin
```

---

## 📈 Relatórios e Analytics

### Dashboard Admin

**Acesso**: `/painel/`

**Mostra:**
- Total de jogadores
- Torneios este mês
- Receita gerada
- Jogadores mais ativos

### Relatório Financeiro

**Acesso**: `/financeiro/dashboard/`

**Análise:**
- Receita por período
- Rake coletado
- Comparação mês a mês
- Exportar dados

### Ranking em Tempo Real

**Acesso**: `/ranking/[season_id]/`

**Funcionalidades:**
- Ranking ao vivo
- Gráfico de evolução
- Comparativo entre jogadores
- Filtros por período

---

## 🎮 Operação de Torneio - Dia D

### 2 horas antes

```
Admin acessa: /torneio/[id]/jogadores/

Verificar:
- [ ] Todas inscrições aprovadas
- [ ] Número de participantes OK
- [ ] Presença confirmada

Ações:
- [ ] Aprova inscrições pendentes
- [ ] Remove inscrições duplicadas
- [ ] Nota no-shows
```

### No horário do torneio

```
Jogadores confirmam presença:
  - Acesso /jogador/confirmar/[tournament_id]/
  - OU Admin marca no sistema

Admin inicia torneio:
  - Sistema começa a rastrear
  - Notifica mudanças de blinds
  - Registra movimento de stacks
```

### Ao encerrar

```
Admin acessa: /torneio/[id]/lancamento/

Lança resultados:
- [ ] Posição de cada jogador
- [ ] Prêmios recebidos
- [ ] Notas especiais (deal, etc)

Sistema:
- [ ] Calcula pontos automaticamente
- [ ] Atualiza ranking
- [ ] Gera relatório financeiro
- [ ] Notifica jogadores
```

---

## 🔧 Troubleshooting Rápido

### Problema: "Não consigo ver os torneios"

**Solução**: 
1. Verifique se está logado (icone no canto superior)
2. Verifique a temporada (deve estar ATIVA)
3. Crie um torneio em uma temporada ativa

### Problema: "Rank não atualiza"

**Solução**:
1. Verifique se resultado foi lançado
2. Acesse `/painel/` e procure por "Recalcular Ranking"
3. Atualize a página

### Problema: "Jogador não consegue se inscrever"

**Solução**:
1. Verifique se jogador está vinculado a um User
2. Verifique se é um torneio AGENDADO (não encerrado)
3. Tente inscrever manualmente via admin

### Problema: "Qual é a senha do admin?"

**Solução**: Resetar senha via terminal:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='admin')
>>> u.set_password('nova_senha')
>>> u.save()
>>> exit()
```

---

## 🎯 Customizações Comuns

### Mudar cores/tema

**Arquivo**: `core/templates/base.html`

```css
/* Linha ~30 */
:root {
    --primary-color: #007bff;      /* Azul padrão */
    --sidebar-width: 260px;
}
```

**Mudar para verde:**
```css
--primary-color: #28a745;
```

### Adicionar logo do clube

**Arquivo**: `core/templates/base.html`

```html
<!-- Linha ~250 -->
<a class="navbar-brand me-auto" href="/">
    <!-- MUDE ISSO: -->
    <i class="bi bi-suit-spade-fill"></i> PokerClube
    
    <!-- PARA ISSO: -->
    <img src="/static/images/seu-logo.png" height="30">
</a>
```

### Mudar nome "PokerClube" globalmente

```bash
# No terminal:
find . -type f -name "*.html" -o -name "*.py" | xargs sed -i 's/PokerClube/Seu Club Name/g'
```

---

## 📱 Responder Dúvidas Comuns

### "Posso usar em meu celular?"

**Resposta**: Sim! O sistema é responsivo. Abra em qualquer navegador mobile.

### "Quanto custa manter?"

**Resposta**: Depende do servidor. Cloud mínimo ~R$100/mês. Desenvolvimento: personalizado.

### "Posso integrar com meu website?"

**Resposta**: Sim! Temos API REST disponível. Pode exibir ranking em tempo real no seu site.

### "Como funciona a segurança?"

**Resposta**: 
- Dados isolados por club (multi-tenant)
- Senhas criptografadas
- HTTPS em produção
- Auditoria de ações

### "Quanto tempo leva para implementar?"

**Resposta**: 
- Setup básico: 1 dia
- Treinamento: 1 dia
- Primeiros torneios: já rodando

### "Preciso saber programar?"

**Resposta**: Não! O sistema tem interface visual para tudo. Desenvolvimento apenas se quiser customizações.

---

## 📞 Checklist de Onboarding

### Dia 1: Instalação
- [ ] Sistema instalado e rodando
- [ ] Admin criado
- [ ] Banco de dados funcionando
- [ ] Teste de acesso remoto

### Dia 2: Configuração
- [ ] Logo/cores customizadas
- [ ] Temporada criada
- [ ] Tipos de torneio definidos
- [ ] Estruturas de blind carregadas

### Dia 3: Dados
- [ ] Jogadores cadastrados
- [ ] Admins/moderadores criados
- [ ] Permissões configuradas
- [ ] Teste de fluxo completo

### Dia 4: Primeiro Evento
- [ ] Primeiro torneio criado
- [ ] Inscrições funcionando
- [ ] Resultados lançados
- [ ] Ranking atualizado

### Dia 5: Go Live
- [ ] Jogadores acessando sistema
- [ ] Feedback coletado
- [ ] Ajustes implementados
- [ ] Suporte preparado

---

## 📚 Recursos Adicionais

### Documentação Completa
- Guia de Usuário: `/docs/USUARIO_MANUAL.md`
- Referência Técnica: `/docs/DOCUMENTACAO_TECNICA.md`
- FAQ: `/docs/FAQ.md`

### Videos de Treinamento
- Setup e primeiros passos: YouTube
- Operação de torneios: YouTube
- Análise de relatórios: YouTube

### Comunidade
- Forum: forum.pokerclube.com
- Chat: discord.gg/pokerclube
- Email: suporte@pokerclube.com

---

## 🚀 Próximos Passos

1. **Experimentar**: Use o sistema com dados de teste
2. **Feedback**: Nos diga o que gostaria de adicionar
3. **Customizar**: Adaptamos cores, campos, etc
4. **Deploy**: Subimos em produção
5. **Treinar**: Suas equipes usam o sistema
6. **Escalar**: Adiciona novos clubs/torneios

---

## 📞 Suporte

**Email**: contato@pokerclube.com
**Whatsapp**: +55 (XX) 9XXXX-XXXX
**Website**: pokerclube.com
**Documentação**: docs.pokerclube.com

---

**PokerClube v1.0** - Gestão Inteligente de Torneios de Poker
Últimas atualizações: Dezembro de 2025
