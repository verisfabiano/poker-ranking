# 🧪 GUIA DE TESTES - PHASE 1 PLAYER DASHBOARD

## ✅ Checklist de Verificação

### 1. Acesso à Dashboard
- [ ] Logar como jogador (não admin)
- [ ] Acessar `/player/home/` ou clique no link "Home"
- [ ] Verificar que não há erro 404 ou 500

### 2. Seção: Resumo Financeiro
- [ ] Ver 4 cards azulejados com ícones
- [ ] Card 1: "Gasto Total" em vermelho
- [ ] Card 2: "Ganho Total" em verde
- [ ] Card 3: "Saldo Líquido" (verde se positivo, vermelho se negativo)
- [ ] Card 4: "ROI" com percentual
- [ ] Todos mostram valores numéricos (não vazios)
- [ ] Hover effect funciona (sombra aumenta)

### 3. Seção: Estatísticas Gerais
- [ ] Ver 3 cards informativos
- [ ] Card "Participações": mostra número de torneios
- [ ] Card "Participações": mostra rebuys e add-ons
- [ ] Card "Colocações": mostra 1º, Top 3, Top 10 em grid
- [ ] Card "Performance": mostra taxa ITM em %

### 4. Seção: Posição no Ranking
- [ ] Ver card grande com ranking info
- [ ] Número de posição em destaque (#1, #2, etc)
- [ ] Mensagem "de X jogadores"
- [ ] Campo "Pontos Acumulados" visível
- [ ] Botão "[Ver Ranking Completo]" funciona

**Se sem dados de ranking:**
- [ ] Mensagem: "Você ainda não está no ranking desta temporada"
- [ ] Sugestão: "Complete um torneio para entrar!"

### 5. Seção: Últimos Resultados
- [ ] Tabela com até 10 resultados
- [ ] Colunas: Torneio, Data, Tipo, Posição, Prêmio
- [ ] Posições com badges coloridas:
  - [ ] 1º lugar: 🥇 (verde)
  - [ ] 2-3º lugar: 🥈/🥉 (azul)
  - [ ] 4-10º lugar: (azul)
  - [ ] 11+º lugar: (cinza)
- [ ] Prêmios mostram corretamente
- [ ] Data formatada (dd/mm/yyyy)

**Se sem resultados:**
- [ ] Mensagem: "Nenhum resultado registrado"

### 6. Responsividade
- [ ] **Mobile (320px):**
  - [ ] Cards empilhados verticalmente
  - [ ] Tabela scrollável horizontal
  - [ ] Sem cortes ou overflow
  
- [ ] **Tablet (768px):**
  - [ ] 2 colunas de cards
  - [ ] Tabela com scroll se necessário
  
- [ ] **Desktop (1200px+):**
  - [ ] 3-4 colunas de cards
  - [ ] Tabela completa visível
  - [ ] Alinhamento perfeitamente

### 7. Elementos Originais
- [ ] Header com saudação "Bem-vindo, [nome]!"
- [ ] Botão "Ver Torneios"
- [ ] Seção "Temporadas Ativas" ainda visível
- [ ] Seção "Próximos Torneios" ainda visível
- [ ] Seção "Minhas Inscrições" ainda visível

### 8. Performance
- [ ] Carregamento rápido (< 2 segundos)
- [ ] Sem mensagens de erro no console
- [ ] Sem warnings no browser
- [ ] Hover effects suaves (não travado)

---

## 📊 Testes de Dados

### Teste 1: Jogador Sem Participações
**Preparação:** Crie novo jogador sem inscrições

**Verificar:**
- [ ] Gasto Total: R$ 0,00
- [ ] Ganho Total: R$ 0,00
- [ ] Saldo Líquido: R$ 0,00 (cinza/neutro)
- [ ] ROI: 0,0%
- [ ] Participações: 0 torneios
- [ ] Sem resultados na tabela
- [ ] Mensagem no ranking: "Você ainda não está no ranking"

---

### Teste 2: Jogador Com Algumas Participações
**Preparação:** Crie participações e resultados

**Verificar:**
- [ ] Gasto Total > 0
- [ ] Ganho Total > 0 (se houver prêmios)
- [ ] Saldo Líquido = Ganho - Gasto
- [ ] ROI = (Saldo / Gasto) × 100
- [ ] Participações conta corretamente
- [ ] Colocações mostra 1º, Top 3, Top 10
- [ ] Taxa ITM > 0%
- [ ] Últimos resultados aparecem na tabela

---

### Teste 3: Jogador Com Bom Performance
**Preparação:** Crie participações com muitos 1º/2º lugares

**Verificar:**
- [ ] Saldo Líquido positivo (verde)
- [ ] ROI positivo (%)
- [ ] Taxa ITM alta (80%+)
- [ ] Primeiro_lugar > 0
- [ ] Tabela mostra múltiplos 🥇 e prêmios altos

---

### Teste 4: Jogador Com Performance Ruim
**Preparação:** Crie participações sem prêmios

**Verificar:**
- [ ] Saldo Líquido negativo (vermelho)
- [ ] ROI negativo (%)
- [ ] Taxa ITM baixa (< 50%)
- [ ] Prêmios mostram "-" para zereiros
- [ ] Cor vermelha no saldo (alerta visual)

---

## 🌐 Testes Multi-Tenant

- [ ] Logar com jogador do Tenant A
  - [ ] Ver apenas dados do Tenant A
  
- [ ] Logar com jogador do Tenant B
  - [ ] Ver apenas dados do Tenant B
  
- [ ] Verificar isolamento de dados

---

## 🔐 Testes de Segurança

- [ ] Sem login → Redireciona para login
- [ ] Sem tenant válido → Redireciona ou erro apropriado
- [ ] Jogador A não vê dados de Jogador B
- [ ] Admin não vê dados de jogador diferente

---

## 📱 Testes de Navegação

- [ ] Clique em "[Ver Ranking Completo]" → Vai para ranking_season
- [ ] Clique em "[Ver Torneios]" → Vai para player_tournaments
- [ ] Clique em temporada → Vai para ranking_season
- [ ] Clique em próximo torneio → Vai para confirm_presence
- [ ] Botão voltar do navegador funciona

---

## 🐛 Checklist de Erros Comuns

- [ ] Nenhum erro 404 (template ou URL não encontrado)
- [ ] Nenhum erro 500 (erro de servidor/logica)
- [ ] Nenhuma divisão por zero (ROI, taxa ITM)
- [ ] Nenhum None/undefined na template
- [ ] Nenhum typo em nomes de campos
- [ ] Formatação de valores corretos (R$, %, datas)

---

## 📊 Verificação de Cálculos

### ROI (Return on Investment)
```
Fórmula: (Saldo Líquido / Gasto Total) × 100
Exemplo: (500 / 1000) × 100 = 50%
```

**Testar:**
- [ ] Calcular manualmente
- [ ] Comparar com valor exibido
- [ ] Verificar sinal (+ ou -)

### Taxa ITM (In The Money)
```
Fórmula: (Torneios com Prêmio / Total Torneios) × 100
Exemplo: (8 / 10) × 100 = 80%
```

**Testar:**
- [ ] Contar prêmios > 0
- [ ] Dividir por total
- [ ] Comparar percentual

### Saldo Líquido
```
Fórmula: Ganho Total - Gasto Total
```

**Testar:**
- [ ] Soma prêmios (ganho)
- [ ] Soma buy-ins + rebuys + add-ons (gasto)
- [ ] Subtração correta

---

## 🎨 Verificação Visual

- [ ] Cores corretas (verde = positivo, vermelho = negativo)
- [ ] Ícones visíveis (bi-wallet, bi-graph-up, etc)
- [ ] Badges com cor apropriada
- [ ] Fonts legíveis
- [ ] Espaçamento consistente
- [ ] Alinhamento de elementos

---

## 📈 Performance

| Métrica | Target | Teste |
|---------|--------|-------|
| Carregamento | < 2s | Medir tempo load |
| FCP | < 1.5s | DevTools |
| LCP | < 2.5s | DevTools |
| Queries | < 10 | Django debug |
| Hover lag | < 16ms | Smooth? |

---

## ✅ Aprovação Final

Quando todos os itens estiverem checkados:

- [ ] **Funcionalidade:** Todos os 4 cards funcionando
- [ ] **Dados:** Cálculos corretos
- [ ] **Responsividade:** Funciona em todos os tamanhos
- [ ] **Performance:** Carregamento rápido
- [ ] **Segurança:** Multi-tenant isolado
- [ ] **Visual:** Design consistente e bonito

**Status:** ✅ APROVADO PARA PRODUÇÃO

---

## 📝 Notas de Teste

Use este espaço para anotações durante testes:

```
Data: _______________
Testador: _______________
Browser: _______________
Device: _______________

Observações:
_____________________________________________
_____________________________________________
_____________________________________________

Issues encontrados:
_____________________________________________
_____________________________________________

Aprovado em: _______________
```

---

**Happy Testing! 🎉**

Se encontrar qualquer problema, documente com:
- [ ] Screenshot
- [ ] Passos para reproduzir
- [ ] Valor esperado vs real
- [ ] Browser/Device usado
