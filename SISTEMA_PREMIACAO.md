# Sistema de Divisão de Premiação - Documentação

## 📋 Visão Geral

O sistema de divisão de premiação permite que o diretor do torneio distribua os prêmios de forma flexível após a finalização do torneio. Suporta dois modos:

1. **Modo Percentual**: Distribuir prêmios como percentual do pote total
2. **Modo Fixo**: Definir valores em reais para cada posição

## 🎯 Características Principais

### ✅ Dois Modos de Operação

#### Modo Percentual
- Ideal para torneios com pote variável
- Calcular automaticamente baseado em % do pote
- Exemplo: 50% para 1º, 30% para 2º, 20% para 3º
- **Vantagem**: Se o pote mudar, os percentuais se ajustam automaticamente

#### Modo Fixo
- Ideal para tornei com premiação predeterminada
- Digitar valores em reais manualmente
- Exemplo: 1º lugar ganha R$ 500, 2º ganha R$ 300, etc
- **Vantagem**: Total controle sobre cada prêmio

### 📊 Templates Pré-definidos

O sistema vem com 8 templates prontos:

**Para Torneios Pequenos (18-30 jogadores):**
1. **Top 3 Clássico** (50/30/20) - 18-23 jogadores
2. **Top 4 Balanceado** (42/28/18/12) - 24-27 jogadores
3. **Top 4 Agressivo** (45/25/15/15) - Alternativa mais agressiva
4. **Top 5 Distribuído** (35/23/17/13/12) - 28-30 jogadores

**Para Torneios Maiores:**
5. **Top 6 Grandes Eventos** (30/20/15/12/12/11) - 40+ jogadores
6. **Top 8 Mega Eventos** (25/17/13/11/10/10/9/5) - 50+ jogadores

**Modo Fixo (Customizável):**
7. **Top 3 Fixo** - 3 posições, R$ 500/300/200 (exemplo)
8. **Top 4 Fixo** - 4 posições, R$ 500/300/150/50 (exemplo)

### 🔧 Cálculo Automático do ITM

O sistema recomenda automaticamente quantas posições devem ser premiadas:
- **Regra Padrão**: 15% do field (In The Money)
- **Mínimo**: 3 posições
- **Casos especiais**: Ajusta para muito poucos ou muitos jogadores

### 💰 Cálculo do Pote

O pote é calculado automaticamente como:

```
Pote = (Buy-in + Rebuys + Rebuy Duplo + Add-on + Staff) - Rake Total
```

### ✓ Validações

O sistema valida automaticamente:
- ✅ Total distribuído corresponde ao pote (com tolerância de 10 centavos)
- ✅ Todas as posições têm valores definidos
- ✅ Percentuais estão entre 0 e 100
- ✅ Valores são positivos

## 🚀 Como Usar

### Passo 1: Acessar o Sistema

1. Ir para **Torneios > Dashboard**
2. Encontrar o torneio com status **ENCERRADO**
3. Clicar em **Distribuir Prêmios** ou **Premiação**

### Passo 2: Selecionar Modo

Escolha entre:
- **Percentual do Pote** (padrão)
- **Valores Fixos (R$)**

### Passo 3: Usar Template ou Customizar

**Opção A - Usar Template:**
1. Clicar em um dos botões de template sugerido
2. Sistema carrega automaticamente os percentuais/valores
3. Editar conforme necessário

**Opção B - Customizar:**
1. Definir número de premiados (ITM count)
2. Digitar percentual ou valor para cada posição
3. Sistema calcula automaticamente os valores

### Passo 4: Revisar e Finalizar

1. Verificar o resumo de distribuição
2. Validar que total = pote
3. Clicar em **Finalizar Distribuição**
4. Confirmar (não pode ser desfeito)

## 📊 Exemplos Práticos

### Exemplo 1: Torneio Pequeno (20 jogadores, R$ 100 buy-in)

```
Total Arrecadado: 20 × R$ 100 = R$ 2.000
Rake (10%): -R$ 200
Pote: R$ 1.800

Distribuição (Top 3 Clássico):
1º lugar: 50% × R$ 1.800 = R$ 900
2º lugar: 30% × R$ 1.800 = R$ 540
3º lugar: 20% × R$ 1.800 = R$ 360
Total: R$ 1.800 ✓
```

### Exemplo 2: Torneio com Rebuys (25 jogadores)

```
Entradas:
- Buy-in: 25 × R$ 100 = R$ 2.500
- Rebuys (8 × 2 cada): 16 × R$ 100 = R$ 1.600
- Add-on (15): 15 × R$ 100 = R$ 1.500
Total: R$ 5.600

Rake (10%): -R$ 560
Pote: R$ 5.040

Distribuição (Top 4 Balanceado):
1º: 42% × R$ 5.040 = R$ 2.117
2º: 28% × R$ 5.040 = R$ 1.411
3º: 18% × R$ 5.040 = R$ 907
4º: 12% × R$ 5.040 = R$ 605
Total: R$ 5.040 ✓
```

### Exemplo 3: Modo Fixo (Premiação Predeterminada)

```
Diretor digita:
1º lugar: R$ 2.000
2º lugar: R$ 1.200
3º lugar: R$ 800
Total: R$ 4.000
```

## 📈 Regras de Premiação (Prática)

### Para Torneios Pequenos (18-30 jogadores)

**Quantidade de Premiados:**
- 18-23 jogadores: **3 posições**
- 24-27 jogadores: **4 posições**
- 28-30 jogadores: **5 posições**

**Distribuição de Percentuais:**

| Posição | 3 Premiados | 4 Premiados | 5 Premiados |
|---------|-----------|-----------|-----------|
| 1º | 50% | 42-45% | 35% |
| 2º | 30% | 25-28% | 23% |
| 3º | 20% | 15-18% | 17% |
| 4º | - | 10-12% | 13% |
| 5º | - | - | 12% |

### Para Torneios Maiores (50+ jogadores)

- **ITM**: 15% do field (aprox.)
- **Padrão**: Top 8 a Top 20
- **Distribuição**: Mais "achatada" porque paga muitas pessoas
- **Mesa Final**: Concentra ~50-60% do pote

## 🎁 Conceito de "Salva" (Bubble)

Em clubes pequenos, é comum dar uma "salva" (valor mínimo) para o jogador que sofre "bubble" (fica fora do dinheiro por pouco).

**Como Implementar:**
1. Usar o último lugar premiado como R$ 0,00 (vazio)
2. Distribuir esse valor manualmente para o bubble
3. Ou usar os valores de forma que o bubble receba ~1x buy-in

## 🔐 Segurança e Histórico

- Uma vez finalizada, a distribuição **não pode ser editada**
- Todos os registros ficam no sistema para auditoria
- Admin pode visualizar histórico completo
- Prêmios podem ser marcados como "Pago" após distribuição

## 📋 Status e Próximas Ações

- **Em Edição**: Pode adicionar/remover prêmios
- **Finalizado**: Locked, pronto para pagamentos
- **Pago**: Marcar como "Pago" após entregar ao jogador

## 🆘 Troubleshooting

### "Total distribuído não bate com o pote"
- Verificar soma de todos os percentuais/valores
- Deve ser bem próximo (até 10 centavos de diferença)
- Usar arredondamento manual se necessário

### "Não consigo editar depois de finalizar"
- Distribuição é irreversível por segurança
- Para alterar, criar nova distribuição (se permitido)

### "Template não aparece"
- Verificar se o template está ativo (não desativado)
- Verificar se ITM count corresponde ao número de premiados

## 📞 Suporte

Para dúvidas sobre premiaçõespg, consulte:
- Documentação no sistema
- Templates pré-definidos (estudar exemplos)
- Admin panel para histórico

---

**Versão**: 1.0  
**Data**: Dezembro 2025  
**Status**: Ativo e Testado
