# 📊 DADOS DE TESTE POPULADOS - GUIA DE ACESSO

## ✅ Status da População de Dados

**Data**: 19 de Dezembro de 2025  
**Status**: ✓ Dados populados com sucesso!

### Resumo dos Dados Criados

```
✓ Tenant: Clube Poker Teste
✓ Jogadores: 15
✓ Temporadas: 2 (2024 e 2025)
✓ Torneios: 10 (5 por temporada)
✓ Resultados: 114
✓ Estatísticas: 30
✓ Prêmios distribuídos: R$ 11.500,00
```

---

## 📱 URLs DE ACESSO AO SISTEMA

### RANKING

| URL | Descrição |
|-----|-----------|
| `http://localhost:8000/ranking/` | **Ranking Geral** - Todas as temporadas |
| `http://localhost:8000/ranking/10/` | **Ranking 2024** - Temporada 2024 |
| `http://localhost:8000/ranking/11/` | **Ranking 2025** - Temporada 2025 |
| `http://localhost:8000/ranking/10/avancado/` | **Ranking Avançado 2024** - Estatísticas detalhadas |
| `http://localhost:8000/ranking/11/avancado/` | **Ranking Avançado 2025** - Estatísticas detalhadas |

### FINANCEIRO

| URL | Descrição |
|-----|-----------|
| `http://localhost:8000/financeiro/dashboard/` | **Dashboard Financeiro** - Visão geral de receitas e despesas |

### DETALHES DOS TORNEIOS

Para acessar os detalhes financeiros de um torneio específico:
- `http://localhost:8000/torneio/<ID>/financeiro/`

Exemplo:
- `http://localhost:8000/torneio/1/financeiro/`
- `http://localhost:8000/torneio/2/financeiro/`

---

## 🏆 TOP 10 JOGADORES POR TEMPORADA

### Temporada 2025

| Posição | Jogador | Pontos | Torneios | Vitórias | ROI | ITM |
|---------|---------|--------|----------|----------|-----|-----|
| 1 | Diego | 27 | 4 | 1 | 80.0% | 75.0% |
| 2 | Rafa | 26 | 5 | 1 | -16.7% | 60.0% |
| 3 | Vitão | 22 | 4 | 1 | 14.3% | 50.0% |
| 4 | Charlie | 20 | 3 | 0 | -25.0% | 66.7% |
| 5 | Pedoca | 19 | 4 | 1 | 16.7% | 75.0% |

### Temporada 2024

| Posição | Jogador | Pontos | Torneios | Vitórias | ROI | ITM |
|---------|---------|--------|----------|----------|-----|-----|
| 1 | Marquinhos | 22 | 4 | 1 | -12.5% | 75.0% |
| 2 | Fabiano | 20 | 5 | 1 | -25.0% | 40.0% |
| 3 | Guto | 19 | 5 | 0 | -31.2% | 60.0% |
| 4 | Vitão | 18 | 4 | 0 | 20.0% | 75.0% |
| 5 | Diego | 17 | 3 | 1 | 0.0% | 33.3% |

---

## 🎰 TORNEIOS CRIADOS

### Temporada 2025

1. **Semanal #1 - Quarta** (04/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 15 | Resultados: 15 | Prêmios: R$ 1.150,00

2. **Semanal #2 - Sexta** (17/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 15 | Resultados: 15 | Prêmios: R$ 1.150,00

3. **Especial Sábado** (17/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 12 | Resultados: 12 | Prêmios: R$ 1.150,00

4. **Torneio da Casa** (14/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 9 | Resultados: 9 | Prêmios: R$ 1.150,00

5. **Mega Torneio** (16/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 8 | Resultados: 8 | Prêmios: R$ 1.150,00

### Temporada 2024

1. **Semanal #1 - Quarta** (06/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 11 | Resultados: 11 | Prêmios: R$ 1.150,00

2. **Semanal #2 - Sexta** (16/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 12 | Resultados: 12 | Prêmios: R$ 1.150,00

3. **Especial Sábado** (14/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 11 | Resultados: 11 | Prêmios: R$ 1.150,00

4. **Torneio da Casa** (07/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 8 | Resultados: 8 | Prêmios: R$ 1.150,00

5. **Mega Torneio** (12/12/2025)
   - Buy-in: R$ 100,00
   - Inscritos: 13 | Resultados: 13 | Prêmios: R$ 1.150,00

---

## 👥 JOGADORES CRIADOS

1. João Silva (Joãozinho)
2. Pedro Santos (Pedoca)
3. Carlos Oliveira (Charlie)
4. Lucas Costa (Luc)
5. Felipe Alves (Flip)
6. Marcos Gomes (Marquinhos)
7. Diego Ferreira (Diego)
8. Bruno Martins (Brunão)
9. Rafael Rocha (Rafa)
10. Thiago Pinto (Thiago)
11. Gustavo Souza (Guto)
12. André Ribeiro (André)
13. Tiago Mendes (Tiaguinho)
14. Victor Lima (Vitão)
15. Fabiano Verís (Fabiano)

---

## 🔧 RECURSOS TESTÁVEIS

### 1. **Ranking System**
- ✅ Pontos calculados dinamicamente (baseado em buy-in e posição)
- ✅ Ranking por temporada
- ✅ Ranking avançado com estatísticas detalhadas
- ✅ Top 3, Top 5, Vitórias, ROI, Taxa ITM

### 2. **Financial Dashboard**
- ✅ Entradas (Buy-in + Rebuy + Add-on + Rake)
- ✅ Saídas (Prêmios Pagos)
- ✅ Resultado (Lucro/Prejuízo)
- ✅ Detalhes por torneio

### 3. **Tournament Management**
- ✅ Multiple tournaments with different buy-ins
- ✅ Buy-in, Rebuy, Add-on, e-n registrados
- ✅ Múltiplas posições finais
- ✅ Prêmios distribuídos corretamente

### 4. **Player Statistics**
- ✅ Participações totais
- ✅ Vitórias e posicionamentos top
- ✅ ROI (Return on Investment)
- ✅ Taxa ITM (In The Money)
- ✅ Média de pontos por torneio

---

## 📊 ESTRUTURA DO CÁLCULO DE PONTOS

### Modo DINÂMICO (Atual)

**Fórmula**: `(buy-in / 10) × multiplicador_posição × multiplicador_torneio`

**Multiplicadores por Posição**:
- 1º lugar: 5x
- 2º lugar: 4x
- 3º lugar: 3x
- 4º-5º lugar: 2x
- 6º+ lugar: 1x

**Exemplo**:
- Torneio com buy-in R$ 100
- Jogador finalista em 2º lugar
- Pontos = (100 / 10) × 4 × 1 = **40 pontos**

---

## 💡 COMO USAR ESSES DADOS

### 1. Testar o Ranking
1. Acesse `http://localhost:8000/ranking/11/`
2. Verifique se os jogadores aparecem com pontos corretos
3. Clique em um jogador para ver detalhes

### 2. Testar o Dashboard Financeiro
1. Acesse `http://localhost:8000/financeiro/dashboard/`
2. Veja o total de Entradas, Saídas e Resultado
3. Clique nos torneios para ver detalhes

### 3. Testar o Ranking Avançado
1. Acesse `http://localhost:8000/ranking/11/avancado/`
2. Veja estatísticas completas (vitórias, top 3, ROI, ITM)
3. Confirme se todos os cálculos estão corretos

### 4. Adicionar Novos Dados
Para adicionar mais dados de teste, execute:
```bash
python populate_test_data.py
```

Este script é idempotente (pode ser executado múltiplas vezes sem duplicar dados).

---

## 🐛 Troubleshooting

### Servidor não está rodando?
```bash
python manage.py runserver 0.0.0.0:8000
```

### Limpar e recriar os dados?
```bash
# Cuidado! Isso deleta TODOS os dados
python manage.py flush

# Depois repopular
python populate_test_data.py
```

### Ver resumo dos dados?
```bash
python show_test_data.py
```

---

## 📝 Scripts Disponíveis

| Script | Função |
|--------|--------|
| `populate_test_data.py` | Popula todos os dados de teste |
| `show_test_data.py` | Exibe resumo dos dados populados |
| `rebuild_ranking.py` | Reconstrói o ranking (idempotente) |
| `debug_ranking.py` | Debuga problemas de cálculo de ranking |

---

**Última atualização**: 19/12/2025 às 07:45 UTC  
**Status do Sistema**: ✅ Operacional e pronto para testes
