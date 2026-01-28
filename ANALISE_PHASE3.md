# Phase 3: Wizard para Criar Novos Torneios - Análise

## Status: Planejamento

---

## Problema Atual (Form Atual)

O formulário de criação de torneios (`tournament_form.html`) é **muito grande e complexo**:

```
┌─────────────────────────────────────────┐
│ Informações Básicas                     │
├─────────────────────────────────────────┤
│ Nome | Data/Hora | Tipo de Pontuação   │
├─────────────────────────────────────────┤
│ Buy-in e Rake (Fixo/Percentual/Misto)  │
├─────────────────────────────────────────┤
│ Rebuy e Rebuy Duplo                     │
├─────────────────────────────────────────┤
│ Add-on                                  │
├─────────────────────────────────────────┤
│ Staff (obrigatório?)                    │
├─────────────────────────────────────────┤
│ Timechip                                │
├─────────────────────────────────────────┤
│ Blind Structure                         │
├─────────────────────────────────────────┤
│ Produtos disponíveis (checkboxes)       │
├─────────────────────────────────────────┤
│ Status do torneio                       │
└─────────────────────────────────────────┘
```

**Problemas:**
- ✗ Muitos campos na mesma tela
- ✗ Usuário fica confuso sobre ordem de preenchimento
- ✗ Validações são apenas ao final (no POST)
- ✗ Sem prévia/resumo antes de criar
- ✗ Sem guia clara: por onde começo?

---

## Solução: Wizard de 4 Etapas

### Etapa 1: Informações Básicas
**Título**: "Dados Iniciais do Torneio"

```
┌──────────────────────────────────────────────────┐
│ Qual é o nome e quando será?                     │
├──────────────────────────────────────────────────┤
│ Nome do Torneio: [_____________________]        │
│ Data e Hora:     [_________] [________]        │
│ Tipo de Torneio: [▼ Selecionar] (FIXO apenas) │
└──────────────────────────────────────────────────┘
```

**Validações**:
- Nome obrigatório, mín 3 caracteres
- Data não pode ser no passado
- Tipo obrigatório (se FIXO)

**Próximo**: Avança para Etapa 2

---

### Etapa 2: Configuração de Valores
**Título**: "Buy-in, Rake e Opcionais"

```
┌────────────────────────────────────────────┐
│ Quanto custará participar?                 │
├────────────────────────────────────────────┤
│ Buy-in (R$):        [________]            │
│ Buy-in (Fichas):    [________]            │
│                                             │
│ Rake: ◯ Fixo ◯ % ◯ Fixo+%                │
│ Valor Rake:         [________]            │
│                                             │
│ ☐ Permitir Rebuy?                         │
│   Valor Rebuy:      [________]            │
│ ☐ Permitir Rebuy Duplo?                   │
│   Valor:            [________]            │
│ ☐ Permitir Add-on?                        │
│   Valor:            [________]            │
└────────────────────────────────────────────┘
```

**Validações**:
- Buy-in > 0
- Rake não pode ser 0 (se selecionado)
- Se rebuy = SIM, rebuy_valor obrigatório

**Próximo**: Calcula rake automaticamente, avança Etapa 3

---

### Etapa 3: Configurações Avançadas
**Título**: "Blind Structure, Staff, Timechip"

```
┌────────────────────────────────────────────┐
│ Configurações Adicionais (Opcional)        │
├────────────────────────────────────────────┤
│ Blind Structure: [▼ Selecionar]           │
│                  (↳ Mostra níveis)        │
│                                             │
│ ☐ Obrigatório Staff?                      │
│   Valor Staff:      [________]            │
│   Fichas Staff:     [________]            │
│                                             │
│ ☐ Usar Timechip?                          │
│   Fichas Timechip:  [________]            │
│                                             │
│ Produtos Inclusos:                        │
│ ☐ Produto A (R$ 50)                      │
│ ☐ Produto B (R$ 100)                     │
│ ☐ Produto C (R$ 25)                      │
└────────────────────────────────────────────┘
```

**Validações**:
- Blind structure se selecionado deve ter níveis
- Staff valor > 0 se obrigatório

**Próximo**: Avança para Etapa 4

---

### Etapa 4: Revisão e Confirmação
**Título**: "Confirme os Dados"

```
┌────────────────────────────────────────────────┐
│ RESUMO - Revise antes de criar                 │
├────────────────────────────────────────────────┤
│ BÁSICO                                          │
│ ├─ Nome: Terça Turbo 10K                       │
│ ├─ Data: 28/01/2026 20:00                      │
│ └─ Tipo: Turbo (x1.5)                          │
│                                                 │
│ FINANCEIRO                                      │
│ ├─ Buy-in: R$ 100 (10.000 fichas)             │
│ ├─ Rake: 10% (R$ 10 por jogador)              │
│ ├─ Pote: R$ 90 (90% do buy-in)                │
│ └─ Rebuy: R$ 100 (Permitido)                  │
│                                                 │
│ EXTRAS                                          │
│ ├─ Blind: Turbo (1h 15m)                       │
│ ├─ Staff: R$ 20 (obrigatório)                 │
│ └─ Produtos: 3 itens selecionados             │
└────────────────────────────────────────────────┘
```

**Botões**:
- `[← Anterior]` - Volta para Etapa 3
- `[Criar Torneio]` - POST /api/tournament/create-wizard/

---

## Fluxo Técnico

### 1. GET `/season/<id>/torneios/novo/` (Page Load)
- Renderizar página com wizard modal (como Phase 2)
- Modal começa com Step 1

### 2. AJAX: Cada etapa valida via fetch
- GET `/api/season/<id>/wizard/step/<n>/validate/`
- POST body: campos da etapa anterior
- Retorna: JSON com sucesso/erros + dados para próxima etapa

### 3. Etapa Específica: Pré-calcula valores
- **Etapa 2**: Calcula rake automaticamente quando muda buy-in
- **Etapa 3**: Carrega blind structures do tenant
- **Etapa 4**: Renderiza resumo com todos os valores

### 4. POST Final: Criar Torneio
- POST `/api/season/<season_id>/tournament/create-wizard/`
- Body: JSON com dados de todas as 4 etapas
- Retorna: `{ success: true, tournament_id: 123, redirect_url: ... }`
- JS redireciona para `/torneio/123/admin/`

---

## Views a Criar

### 1. `tournament_create_wizard_step(request, season_id, step)` [GET]
- Retorna: JSON com campos obrigatórios da etapa + dados para validação

### 2. `tournament_create_wizard_save(request, season_id)` [POST]
- Recebe: JSON com todos os dados (4 etapas)
- Valida: Todas as regras de negócio
- Cria: Tournament + produtos associados
- Retorna: JSON com tournament_id ou erros

---

## Template: Modal Wizard

```html
<div class="modal fade" id="wizardTournamentCreate">
    <!-- Progress Bar -->
    <div class="progress">
        <div id="wizardProgress" class="progress-bar">33%</div>
    </div>
    
    <!-- Step 1: Básico -->
    <div id="step1" class="wizard-step active">...</div>
    
    <!-- Step 2: Valores -->
    <div id="step2" class="wizard-step">...</div>
    
    <!-- Step 3: Avançado -->
    <div id="step3" class="wizard-step">...</div>
    
    <!-- Step 4: Revisão -->
    <div id="step4" class="wizard-step">...</div>
    
    <!-- Botões -->
    <div class="modal-footer">
        <button id="btnAnterior">← Anterior</button>
        <button id="btnProximo">Próximo →</button>
        <button id="btnCriar" style="display:none">Criar Torneio</button>
    </div>
</div>
```

---

## JavaScript: Estado do Wizard

```javascript
let wizardData = {
    // Step 1
    nome: '',
    data: '',
    tipo_id: '',
    
    // Step 2
    buyin: 0,
    buyin_chips: 0,
    rake_type: 'PERCENTUAL',
    rake_valor: 0,
    permite_rebuy: false,
    rebuy_valor: 0,
    permite_rebuy_duplo: false,
    rebuy_duplo_valor: 0,
    permite_addon: false,
    addon_valor: 0,
    
    // Step 3
    blind_structure_id: null,
    staff_obrigatorio: false,
    staff_valor: 0,
    timechip_chips: 0,
    produtos_ids: [],
    
    // Metadados
    pote_calculado: 0,
    rake_calculado: 0
};
```

---

## Exemplo de Uso

### Admin cria "Terça Turbo 10K"

```
STEP 1: Informações Básicas
├─ Nome: "Terça Turbo 10K"
├─ Data: 28/01/2026 20:00
└─ Tipo: Turbo
   ↓ [Validar] ✓ OK

STEP 2: Valores
├─ Buy-in: R$ 100
├─ Fichas: 10000
├─ Rake: 10%
│  ├─ Pote = 90
│  └─ Taxa = 10
├─ Rebuy: SIM (R$ 100)
└─ Add-on: SIM (R$ 100)
   ↓ [Validar] ✓ OK

STEP 3: Avançado
├─ Blind Structure: Turbo (1h15)
├─ Staff: SIM (R$ 20)
├─ Timechip: NÃO
└─ Produtos: [Cachaça, Refrigerante]
   ↓ [Validar] ✓ OK

STEP 4: Revisão
├─ Resumo visual com todos dados
├─ Cálculos previsualizados
└─ [Criar Torneio]
   ↓ POST /api/season/1/tournament/create-wizard/
   
RESULTADO:
✓ Torneio criado (ID: 456)
→ Redireciona para /torneio/456/admin/
```

---

## Benefícios vs Form Atual

| Aspecto | Form Atual | Wizard Phase 3 |
|---------|-----------|-----------------|
| **Linhas** | ~700 | ~400 (modal) |
| **UX** | Abrumador | Guiado passo-a-passo |
| **Validação** | Apenas ao final | Em cada step |
| **Erros** | Em alerts genéricos | Inline com dica |
| **Preview** | Sem prévia | Step 4 mostra resumo |
| **Mobile** | Ruim (scroll infinito) | Bom (modal responsiva) |
| **Tempo criação** | ~3 minutos | ~2 minutos |

---

## Próximas Fases (Futura)

- **Phase 4**: Mobile optimization (validar em telas pequenas)
- **Phase 5**: Batch operations (criar múltiplos torneios de uma vez)
- **Phase 6**: Templates de torneio (salvar/reusar configurações)

---

## Conclusão

Phase 3 é uma evolução natural da UX:
- ✅ Reusa padrão de wizard (como Phase 2)
- ✅ Melhora drasticamente a experiência do admin
- ✅ Reduz erros por validações em cada step
- ✅ Mostra preview antes de confirmar

**Estimado**: 2-3 horas de desenvolvimento
