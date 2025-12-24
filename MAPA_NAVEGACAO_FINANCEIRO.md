# 🗺️ MAPA DE NAVEGAÇÃO - FINANCEIRO

## Quick Access Map

```
HOME
 └─ Menu Lateral (Admin)
     └─ FINANCEIRO
         ├─ Dashboard Principal
         │  └─ http://site/financeiro/
         │     → Últimos 30 dias
         │     → Total faturamento
         │     → Total prêmios
         │     → Saldo
         │
         ├─ Por Período (Com Filtro)
         │  └─ http://site/financeiro/periodo/
         │     → Escolhe data início
         │     → Escolhe data fim
         │     → Clica "Filtrar"
         │     → Ve resultados + comparativa
         │
         ├─ Por Temporada
         │  └─ http://site/financeiro/temporada/[ID]/
         │     → Financeiro da temporada toda
         │     → Evolução mês a mês
         │
         └─ Relatório Completo (NOVO)
             └─ http://site/relatorio/financeiro/completo/
                → Período vs Período
                → Top 10 torneios
                → Gráficos
                → Margens análise
```

---

## 🎯 Por Caso de Uso

### "Quero ver quanto ganhei nos últimos 30 dias"
```
1. Login como admin
2. Menu → Financeiro → Dashboard
3. Ver números principais
4. Pronto! ✅
```

### "Quero ver financeiro de um torneio específico"
```
OPÇÃO A (Via menu):
1. Menu → Torneios
2. Clique no torneio
3. Botão azul "📊 Financeiro"

OPÇÃO B (URL direta):
1. http://site/torneio/42/financeiro/
(Substitui 42 pelo ID do torneio)
```

### "Quero comparar dezembro com novembro"
```
1. Menu → Financeiro → Por Período
2. Coloca: 01/11/2025 a 30/11/2025 (novembro)
3. Clica "Filtrar"
4. Anota números
5. Depois coloca: 01/12/2025 a 31/12/2025
6. Clica "Filtrar"
7. Compara manualmente ou...
8. Usa o Relatório Completo (faz automaticamente)
```

### "Quero relátorio profissional para apresentar"
```
1. Menu → Financeiro → Relatório Completo
2. Ou direto: /relatorio/financeiro/completo/
3. Mostra comparativa automática
4. Tem gráficos
5. Pronto para imprimir/share
```

### "Preciso checar se os valores batem"
```
1. Vá para torneio: /torneio/42/financeiro/reconciliar/
2. Sistema verifica:
   - O que você cobrou
   - O que foi recebido (admin confirmou?)
   - Se tem discrepâncias
3. Gera relatório de conferência
```

---

## 📊 Estrutura de Dados (O que você vê)

```
RECEITA (o que entra)
│
├─ Buy-ins
│  └─ Qtde jogadores × valor buy-in
│
├─ Rebuys
│  └─ Qtde rebuys × valor
│
├─ Add-ons
│  └─ Qtde add-ons × valor
│
├─ Produtos (Jackpot, Bounty, etc)
│  └─ Qtde × valor produto
│
└─ TOTAL RECEITA

CUSTOS (o que sai)
│
├─ Rake (sua margem cobrada)
│  └─ Fixo OU Percentual OU Misto
│
├─ Prêmios Pagos
│  └─ 1º lugar + 2º lugar + 3º lugar + ...
│
└─ TOTAL CUSTOS

RESULTADO
│
├─ Saldo = Receita - Custos
├─ Margem = Rake / Receita × 100
└─ Status = OK / ATENÇÃO / ERRO
```

---

## 🔄 Fluxo de Atualização (Como os números mudam)

```
ANTES DO TORNEIO
├─ Torneio criado (R$ 0 - sem inscritos)
└─ Números = 0

DURANTE INSCRIÇÕES
├─ Jogador A se inscreve (buy-in R$ 100)
├─ Números atualizam: Receita = R$ 100
├─ Jogador B se inscreve (buy-in R$ 100)
├─ Números atualizam: Receita = R$ 200
└─ ... mais inscritos ...

INICIO DO TORNEIO
├─ Admin confirma inscrições
├─ Rake é cobrado
├─ Números: Receita - Rake = Pote

DURANTE TORNEIO
├─ Alguém faz rebuy (R$ 100)
├─ Números atualizam (receita +R$ 100)
└─ Alguém compra bounty (R$ 50)
    └─ Números atualizam (receita +R$ 50)

FINALIZANDO
├─ 1º lugar: prêmio R$ 500
├─ 2º lugar: prêmio R$ 300
├─ 3º lugar: prêmio R$ 100
└─ Números atualizam (custos = R$ 900)

APÓS FINAL
├─ Saldo calculado = Receita - Custos
├─ Margem calculada = Rake / Receita
└─ Status final exibido
```

---

## 🎨 Exemplo Visual (Como fica a tela)

```
┌──────────────────────────────────────────────────────────┐
│ 📈 FINANCEIRO - ÚLTIMOS 30 DIAS                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐        │
│  │ FATURAMENTO BRUTO   │  │ RAKE COBRADO        │        │
│  │                     │  │                     │        │
│  │    R$ 5.000,00      │  │    R$ 500,00        │        │
│  │                     │  │                     │        │
│  │ 8 torneios, 45 players                       │        │
│  └─────────────────────┘  └─────────────────────┘        │
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐        │
│  │ POTE PRÊMIOS        │  │ PRÊMIOS PAGOS       │        │
│  │                     │  │                     │        │
│  │    R$ 4.500,00      │  │    R$ 4.200,00      │        │
│  │                     │  │                     │        │
│  │ Após rake           │  │ Segundo results     │        │
│  └─────────────────────┘  └─────────────────────┘        │
│                                                           │
│  ┌──────────────────────────────────────────────┐        │
│  │ SALDO DO PERÍODO: R$ 300,00 ✅              │        │
│  │ MARGEM: 10%                                  │        │
│  └──────────────────────────────────────────────┘        │
│                                                           │
│  [Filtrar por período] [Ver relatório] [Exportar]        │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Atalhos (Marque seus favoritos)

**Local Dev:**
```
http://localhost:8000/financeiro/
http://localhost:8000/financeiro/periodo/
http://localhost:8000/relatorio/financeiro/completo/
```

**Produção:**
```
https://pokerranking.com/financeiro/
https://pokerranking.com/financeiro/periodo/
https://pokerranking.com/relatorio/financeiro/completo/
```

---

## 🔗 Links Rápidos por Torneio

Quando você tá vendo um torneio:
```
Torneio: Aberto de Taubate #15
├─ [Ver Ranking]
├─ [📊 Financeiro]  ← CLICA AQUI para ir direto
├─ [Inscritos]
├─ [Resultados]
└─ [Editar]
```

Clicando em "📊 Financeiro":
```
→ Abre /torneio/15/financeiro/
→ Mostra dados específicos desse torneio
```

---

## 📱 Menu Sidebar (Localização)

```
Esquerda da tela:
│
├─ HOME
├─ TORNEIOS
│  ├─ Próximos
│  ├─ Finalizados
│  └─ Criar novo
│
├─ RANKING
│  ├─ Geral
│  └─ Por temporada
│
├─ ✨ FINANCEIRO  ← AQUI ESTÁ!
│  ├─ Dashboard
│  ├─ Por Período
│  ├─ Por Temporada
│  └─ Relatório Completo
│
├─ TEMPORADAS
├─ CONFIGURAÇÕES
└─ LOGOUT
```

---

## ✅ Checklist de Acesso

```
□ Login? (SIM = continuar | NÃO = login primeiro)
□ Admin? (is_staff=True)
□ Clicou em "FINANCEIRO" no menu?
□ Escolheu uma opção?
□ Números aparecem?
□ Quer filtrar? (vai em "Por Período")
□ Quer relatório? (vai em "Relatório Completo")

Se tudo OK: ✅ Acesso funcionando!
```

---

## 🆘 Rápida Solução

| Problema | Solução |
|----------|---------|
| "404 not found" | Verifique URL digitada |
| "403 Forbidden" | Você é admin? (is_staff) |
| "Números zerados" | Nenhum torneio no período |
| "Valores diferentes" | Alguns resultados não foram lançados |
| "Página branca" | Refresh (F5) ou clear cache |
| "Não vejo menu" | Login de novo / limpa cookies |

---

**Dica:** Salve os links em favoritos para rápido acesso! 🌟

```
Financeiro: Ctrl+D (ou Cmd+D no Mac)
```
