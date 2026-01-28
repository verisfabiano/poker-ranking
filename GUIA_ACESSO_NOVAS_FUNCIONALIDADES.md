# 🎯 GUIA DE ACESSO ÀS NOVAS FUNCIONALIDADES (Phases 1-6)

## Sumário Rápido

Todos os menus e botões de acesso às novas funcionalidades estão implementados e visíveis para o admin.

---

## 📍 Locais de Acesso (Interface Visual)

### **1. Dashboard do Torneio** (`/torneio/{id}/admin/`)

#### Dropdown "Ações" (Canto Superior Direito)
```
┌─────────────────────────────────────────┐
│ ⚙️ Ações ▼                              │
├─────────────────────────────────────────┤
│ Phase 5: Criação em Lote                │
│ ├─ 📋 Duplicar Torneio                 │
│ ├─ 🔖 Salvar como Template             │
│ ├─────────────────────                 │
│ Phase 6: Recursos Avançados             │
│ ├─ 📅 Criar Série Recorrente           │
│ ├─ ↶ Desfazer Última Ação (se houver)  │
│ ├─────────────────────                 │
│ └─ ✏️ Editar Torneio                   │
└─────────────────────────────────────────┘
```

**O que cada opção faz:**

| Opção | Atalho | Descrição |
|-------|--------|-----------|
| **Duplicar Torneio** | [Dashboard > Ações > Duplicar] | Cria cópia do torneio com mesma config, permite mudar nome/data |
| **Salvar como Template** | [Dashboard > Ações > Salvar Template] | Salva configuração para reutilizar em novos torneios |
| **Criar Série** | [Dashboard > Ações > Série Recorrente] | Cria N torneios automaticamente (semanal/mensal) |
| **Desfazer** | [Dashboard > Ações > Desfazer] | Desfaz última ação realizada (se existir) |
| **Editar** | [Dashboard > Ações > Editar] | Abre tela de edição do torneio |

---

### **2. Listagem de Torneios da Temporada** (`/season/{id}/torneios/`)

#### Dropdown "Ações Rápidas" (Topo da Página)
```
┌──────────────────────────────────────────────┐
│ ⚡ Ações Rápidas ▼   🔄 Atualizar  ➕ Novo   │
├──────────────────────────────────────────────┤
│ Phase 5: Criação em Lote                     │
│ ├─ ☁️ Importar CSV                          │
│ ├─ 📅 Criar Série Recorrente                │
│ ├─────────────────────                      │
│ Phase 3: Criação Normal                      │
│ └─ ⭕ Novo Torneio (Wizard)                 │
└──────────────────────────────────────────────┘
```

**O que cada opção faz:**

| Opção | Atalho | Descrição |
|-------|--------|-----------|
| **Importar CSV** | [Listagem > Ações Rápidas > Importar] | Faz upload de arquivo CSV com múltiplos torneios |
| **Criar Série** | [Listagem > Ações Rápidas > Série] | Abre wizard para criar série automática |
| **Novo Torneio (Wizard)** | [Listagem > Ações Rápidas > Novo] | Cria novo torneio com wizard 4-step |

#### Dropdown de Cada Torneio (Coluna "Gerenciar")
```
┌─────────────────────────────────────────┐
│ 🔧 (dropdown icon)                      │
├─────────────────────────────────────────┤
│ ✏️ Editar Dados                         │
│ 💰 Financeiro                           │
│ ├─────────────────────                 │
│ Phase 5: Criação em Lote                │
│ ├─ 📋 Duplicar                         │
│ ├─ 🔖 Salvar Template                  │
│ ├─────────────────────                 │
│ 📊 Ver Ranking                          │
│ ├─────────────────────                 │
│ 🖥️ Abrir Telão (Timer)                 │
└─────────────────────────────────────────┘
```

**O que cada opção faz:**

| Opção | Descrição |
|-------|-----------|
| **Duplicar** | Cria cópia deste torneio (mesma config) |
| **Salvar Template** | Salva config deste torneio como template |

---

## 🔗 URLs Diretas (Acesso por Link)

Se preferir acessar direto via URL:

### Phase 5: Criação em Lote

```
# Duplicar torneio específico
GET  /torneio/{tournament_id}/duplicar/

# Importar CSV
GET  /season/{season_id}/torneios/importar-csv/

# Salvar template
GET  /torneio/{tournament_id}/salvar-template/
```

### Phase 6: Recursos Avançados

```
# Criar série recorrente
GET  /season/{season_id}/torneios/serie/

# Editar torneio duplicado
GET  /torneio/{tournament_id}/editar-modelo/

# Desfazer ação (API - fetch)
GET  /api/torneio/{tournament_id}/desfazer/
```

---

## 📋 Fluxos Recomendados

### Fluxo 1: Criar Múltiplos Torneios Iguais (Série)

```
1. Ir para: Listagem de Torneios (Season)
2. Clicar: "Ações Rápidas" → "Criar Série"
3. Preencher:
   - Nome base (ex: "Mega Flop")
   - Recorrência (semanal/mensal)
   - Quantidade (quantos torneios criar)
4. Clicar: "Criar Série"
5. ✓ Pronto! Torneios criados automaticamente
```

### Fluxo 2: Importar Múltiplos Torneios via CSV

```
1. Ir para: Listagem de Torneios (Season)
2. Clicar: "Ações Rápidas" → "Importar CSV"
3. Baixar: Template CSV (botão na página)
4. Preencher: Arquivo Excel/Google Sheets
   Colunas: nome, data, tipo, entrada, rake
5. Upload: Fazer upload do arquivo
6. ✓ Pronto! Resultados mostram sucesso/erros
```

### Fluxo 3: Duplicar Torneio Existente

```
Opção A (Via Dashboard):
1. Abrir: Dashboard do torneio (/torneio/{id}/admin/)
2. Clicar: "Ações" → "Duplicar Torneio"
3. Mudar: Nome e/ou data
4. Confirmar: "Duplicar Torneio"

Opção B (Via Listagem):
1. Abrir: Listagem de torneios
2. Clicar: Ícone de engrenagem (gear) do torneio
3. Selecionar: "Duplicar"
4. Mudar: Nome e/ou data
5. Confirmar: "Duplicar Torneio"

Resultado: Novo torneio criado com mesma config
```

### Fluxo 4: Salvar e Reutilizar Template

```
Etapa 1: Salvar Template
1. Abrir: Dashboard do torneio
2. Clicar: "Ações" → "Salvar como Template"
3. Nome: Dar nome descritivo (ex: "Mega Flop Padrão")
4. Confirmar: "Salvar Template"

Etapa 2: Usar Template (próximo torneio)
1. Ir para: Criar novo torneio (wizard)
2. No Step 1: Selecionar template (se houver)
3. Fields são preenchidos automaticamente
4. Editar apenas: Nome e data
5. Confirmar criação

Nota: Templates salvos em sessão por enquanto
```

### Fluxo 5: Desfazer Ação (Undo)

```
1. Abrir: Dashboard do torneio
2. Se houver ação a desfazer:
   - Clicar: "Ações" → "Desfazer Última Ação"
3. Confirmar: "Tem certeza?"
4. ✓ Ação desfeita! Página atualiza
```

---

## 🎨 Visual das Nuevas Funcionalidades

### Dashboard (Phase 1-2)
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  🎰 Painel do Torneio          Agendado  ⚙️ Ações ▼│
│  Mega Flop - 28/01/2026                            │
│                                                     │
│  ✓ 50% Concluído                                  │
│                                                     │
│  ☐ Torneio Criado      ✓ Agora: 28/01 14:30       │
│  ☐ Jogadores            5 inscritos  [Gerenciar]   │
│  ☐ Premios              3 definidos   [Definir]    │
│  ☐ Finalizado           -             -            │
│                                                     │
│  [Lançar Resultados Modal...]                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Listagem (Phase 5-6)
```
┌──────────────────────────────────────────────────────┐
│ Torneios da Temporada        ⚡ Ações ▼  🔄  ➕ Novo │
│ Mega Season 2026                                    │
│                                                     │
│ Data/Hora      │ Evento      │ Tipo    │ Status     │
├────────────────┼─────────────┼─────────┼────────────┤
│ 28/01 20:00    │ Mega Flop   │ Cashier │ ▶️ Anda... │ 🔧 Duplicar / Salvar
│ 29/01 20:00    │ Turbo Cash  │ Turbo   │ 📅 Agend..│ 🔧 Duplicar / Salvar
│ 30/01 15:00    │ SNG         │ SNG     │ ✅ Final..│ 🔧 (deshabilitado)
│                                                     │
└──────────────────────────────────────────────────────┘
```

---

## 🎓 Tutoriais Rápidos

### Tutorial 1: Importar 10 Torneios via CSV (2 minutos)

```
1. Clique em "Ações Rápidas" → "Importar CSV"
2. Clique em "Baixar Template"
3. Abra em Excel/Google Sheets
4. Preencha com seus dados:
   
   nome              | data      | tipo | entrada | rake
   ─────────────────┼──────────┼──────┼─────────┼──────
   Mega Monday      | 2026-02-03 | 1   | 100     | 10
   Mega Wednesday   | 2026-02-05 | 1   | 100     | 10
   Turbo Friday     | 2026-02-07 | 2   | 50      | 5
   ...              | ...       | ... | ...     | ...

5. Salve arquivo como CSV
6. Volte à página do sistema
7. Faça upload do arquivo
8. Sistema mostra resultado (X criados, Y erros)
```

### Tutorial 2: Criar Série Semanal (3 minutos)

```
1. Clique em "Ações Rápidas" → "Criar Série"
2. Preencha:
   - Nome: "Mega Flop"
   - Data Início: "28/02/2026 20:00"
   - Recorrência: "Semanal"
   - Quantidade: "4" (4 semanas)
   - Entrada: "100"
   - Rake: "10"
3. Veja preview de datas:
   - Mega Flop #1 - 28/02 (terça)
   - Mega Flop #2 - 06/03 (terça)
   - Mega Flop #3 - 13/03 (terça)
   - Mega Flop #4 - 20/03 (terça)
4. Clique "Criar Série"
5. ✓ Pronto! 4 torneios criados
```

### Tutorial 3: Salvar Config como Template (1 minuto)

```
1. Abra torneio que quer usar como template
2. Clique em "Ações" → "Salvar como Template"
3. Digite nome: "Mega Flop Padrão"
4. Clique "Salvar Template"
5. Próximo torneio que criar: 
   - Template é carregado automaticamente
   - Campos preenchidos
   - Só muda nome/data!
```

---

## ✨ Resumo Visual: Onde Estão os Menus?

```
┌─ Dashboard (/torneio/{id}/admin/)
│  └─ Botão "Ações" (canto superior direito)
│     ├─ Duplicar Torneio (Phase 5)
│     ├─ Salvar como Template (Phase 5)
│     ├─ Criar Série (Phase 6)
│     ├─ Desfazer (Phase 6)
│     └─ Editar
│
├─ Listagem (/season/{id}/torneios/)
│  ├─ Botão "Ações Rápidas" (topo página)
│  │  ├─ Importar CSV (Phase 5)
│  │  ├─ Criar Série (Phase 6)
│  │  └─ Novo Torneio (Phase 3)
│  │
│  └─ Gear Icon de cada torneio (tabela)
│     ├─ Duplicar (Phase 5)
│     └─ Salvar Template (Phase 5)
│
└─ Novo Torneio (/season/{id}/torneios/novo/)
   └─ Wizard 4-step (Phase 3)
      ├─ Step 1: Básico
      ├─ Step 2: Valores (auto-calcula)
      ├─ Step 3: Avançado
      └─ Step 4: Review
```

---

## 📊 Status de Implementação

| Funcionalidade | Localização | Status | Visível? |
|---|---|---|---|
| Dashboard | `/torneio/{id}/admin/` | ✓ | ✅ |
| Duplicar | Dashboard > Ações | ✓ | ✅ |
| CSV Import | Listagem > Ações Rápidas | ✓ | ✅ |
| Salvar Template | Dashboard > Ações | ✓ | ✅ |
| Criar Série | Listagem > Ações Rápidas | ✓ | ✅ |
| Desfazer (Undo) | Dashboard > Ações | ✓ | ✅ |
| Wizard Criação | Listagem > Ações Rápidas | ✓ | ✅ |

---

## 🆘 Troubleshooting

### "Não vejo o menu 'Ações' no dashboard"
**Solução:** 
- Faça refresh da página (F5)
- Certifique que está logado como admin
- Verifique URL: `/torneio/{ID}/admin/` (não é edit)

### "Não vejo 'Desfazer' no menu de Ações"
**Solução:**
- Esta opção só aparece se houver ações para desfazer
- Faça uma ação primeiro (editar, criar resultado, etc)
- Volte ao dashboard
- Agora o botão deve aparecer

### "CSV Import não funciona"
**Solução:**
1. Verifique formato do CSV (UTF-8, sem BOM)
2. Verifique colunas obrigatórias:
   - nome, data, tipo, entrada, rake
3. Datas no formato: YYYY-MM-DD (2026-02-28)
4. Tipo: use ID do tipo de torneio (1, 2, etc)
5. Entrada/rake: use . (ponto) como separador decimal

---

**Status:** ✅ Todos os menus implementados e visíveis  
**Última atualização:** 28/01/2026  
**Versão:** 1.0.0
