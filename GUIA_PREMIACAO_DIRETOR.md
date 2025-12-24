# 🎁 Guia Completo - Onde Acessar Premiação

## 📍 Localização dos Links de Premiação

O sistema agora oferece **4 formas diferentes** para o diretor acessar a **Distribuição de Prêmios**:

---

## **1. 📋 Lista de Torneios (Temporada)**
**Arquivo:** `tournaments_list.html`  
**URL:** `/season/<season_id>/torneios/`

### Como acessar:
1. Acesse a Temporada (Season)
2. Visualize a lista de torneios da temporada
3. Procure pelo botão **"🎁 Prêmios"** na coluna de ações

```
┌────────────────────────────────────────────┐
│ Torneio              │ Status  │ Gerenciar │
├────────────────────────────────────────────┤
│ Happy Hour Hold'em   │ AGENDADO│ [👥] [🎁] [🏆] [⚙️] │
│ Thursday Night      │ EM_AND. │ [👥] [🎁] [🏆] [⚙️] │
│ SNG Rápido         │ ENCERR. │ [👥] [🎁] [🏆] [⚙️] │
└────────────────────────────────────────────┘

[👥] = Jogadores
[🎁] = Prêmios (NOVO)
[🏆] = Resultados
[⚙️] = Menu
```

---

## **2. 🏠 Dashboard de Torneios**
**Arquivo:** `tournament_dashboard.html`  
**URL:** `/torneios/dashboard/`

### Como acessar:
1. Acesse o Dashboard de Torneios
2. Navegue até a aba do torneio desejado
3. Clique no botão **"🎁 Prêmios"** no card do torneio

```
┌─────────────────────────────────────┐
│   Tournament Name                   │
│   Status: EM_ANDAMENTO              │
│                                     │
│ [🏆 Resultados] [🎁 Prêmios] [💰 Financeiro] │
└─────────────────────────────────────┘
```

---

## **3. 👨‍⚖️ Sala de Controle (Director Panel)**
**Arquivo:** `director_panel.html`  
**URL:** `/torneio/<id>/diretor/`

### Como acessar:
1. Abra a Sala de Controle (Director Panel)
2. Na barra de ações superior, clique em **"🎁 Prêmios"**

```
┌─────────────────────────────────────────────────┐
│ Sala de Controle - Tournament Name              │
│                                                 │
│ [← Sair] [👥 Jogadores] [🎁 Prêmios] [📺 Telão] │
│                                                 │
│ ┌────────────────────────────────────────────┐ │
│ │            ⏰ NÍVEL 3                       │ │
│ │                                            │ │
│ │         100 / 200                          │ │
│ │         ANTE: 20                           │ │
│ │                                            │ │
│ │ [◄◄] [▶️ Pausar/Iniciar] [►►]             │ │
│ └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## **4. 📊 Lista Geral de Todos os Torneios**
**Arquivo:** `tournaments_list_all.html`  
**URL:** `/torneios/`

### Como acessar:
1. Acesse a listagem completa de torneios
2. Procure pelo torneio desejado
3. Clique no botão **"🎁 Prêmios"** à direita

```
┌──────────────────────────────────────────────┐
│ Data      │ Evento          │ Tipo │ Ações  │
├──────────────────────────────────────────────┤
│ 18/12/25  │ Happy Hour      │ Cash │ [...] │
│           │                 │      │ [👥] [🎁] [🏆] │
├──────────────────────────────────────────────┤
│ 17/12/25  │ Thursday Night  │ MTT  │ [...] │
│           │                 │      │ [👥] [🎁] [🏆] │
└──────────────────────────────────────────────┘
```

---

## 🎯 Fluxo de Trabalho Recomendado

### **Durante o Torneio:**
1. Abra a **Sala de Controle** (Director Panel)
2. Use o Timer para controlar os níveis de blinds
3. Use o botão **"👥 Jogadores"** para confirmar Time Chips
4. Abra o **"📺 Telão"** em uma TV/Tela separada

### **Após o Torneio Finalizar:**
1. Vá para **"🏆 Resultados"** para registrar as posições dos jogadores
2. Clique em **"🎁 Prêmios"** para distribuir os prêmios
3. Configure o modo de distribuição (Percentual ou Fixo)
4. Selecione quantos jogadores recebem prêmios (ITM)
5. Finalize a distribuição

---

## 📱 Tela de Distribuição de Prêmios

Ao clicar em qualquer botão **"🎁 Prêmios"**, você será levado para:

**URL:** `/torneio/<tournament_id>/premiacao/`

### Componentes principais:

```
┌─────────────────────────────────────────────────────┐
│ Distribuição de Prêmios - Tournament Name           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ POTE TOTAL: R$ 5.000,00                             │
│                                                     │
│ [Modo Percentual] [Modo Fixo]                       │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Quantidade de Vencedores (ITM): [  5  ]         │ │
│ │                                                 │ │
│ │ Posição │ Percentual │ Valor       │ Jogador    │ │
│ │─────────┼────────────┼─────────────┼────────────│ │
│ │ 1º      │ 50% │      │ R$ 2.500,00 │ [Jogador]  │ │
│ │ 2º      │ 30% │      │ R$ 1.500,00 │ [Jogador]  │ │
│ │ 3º      │ 20% │      │ R$ 1.000,00 │ [Jogador]  │ │
│ │ 4º      │ 0%  │      │ R$ 0,00     │ [Vazio]    │ │
│ │ 5º      │ 0%  │      │ R$ 0,00     │ [Vazio]    │ │
│                                                     │
│ Total Distribuído: R$ 5.000,00                      │
│ Diferença: R$ 0,00 ✅                              │
│                                                     │
│ [Salvar] [Cancelar] [Finalizar & Bloquear]         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features da Distribuição de Prêmios

✅ **Modo Percentual**: Distribuir como % do pote total  
✅ **Modo Fixo**: Distribuir valores exatos em R$  
✅ **Templates Predefinidos**: 8 modelos prontos  
✅ **Cálculo Automático de Pote**: Leva rake em conta  
✅ **Recomendação de ITM**: Sugestão automática  
✅ **Validação de Distribuição**: Garante que não sobre/falte  
✅ **Bloquear Estrutura**: Impede edição após finalizar  

---

## 🔒 Regras Importantes

| Situação | Ação Permitida |
|----------|---|
| Torneio AGENDADO | ❌ Não pode distribuir prêmios |
| Torneio EM_ANDAMENTO | ⚠️ Pode distribuir, mas não recomendado |
| Torneio ENCERRADO | ✅ Distribuição normal |
| Torneio CANCELADO | ❌ Não pode distribuir |
| Prêmios JÁ FINALIZADOS | 🔒 Bloqueado (não pode editar) |

---

## 💡 Dicas

1. **Antes de finalizar**, sempre confirme se os totais batem
2. **Use templates** para agilizar o processo
3. **Finalize apenas após tem certeza** - não pode ser desfeito
4. **Verifique o ITM recomendado** do sistema
5. **Teste com modo percentual primeiro** - é mais flexível

---

## 📞 Suporte

Para dúvidas sobre distribuição de prêmios:
- Consulte a documentação em `SISTEMA_PREMIACAO.md`
- Entre em contato com o suporte
- Acesse o painel administrativo para auditar histórico

---

**Última atualização:** 18/12/2025  
**Versão:** 1.0
