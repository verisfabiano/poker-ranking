# 💰 GUIA DE ACESSO - FUNCIONALIDADES FINANCEIRAS

## 📊 O que foi implementado no Financeiro?

Criamos **2 módulos completos:**

### 1️⃣ **FINANCIAL.PY** (Cálculos básicos)
- Calcular financeiro de um torneio
- Dashboard financeiro (últimos 30 dias)
- Financeiro por temporada
- Financeiro por período customizado

### 2️⃣ **FINANCIAL_ENHANCED.PY** (Avançado)
- Reconciliação automática de caixa
- Relatório financeiro completo com comparativas
- Fluxo de caixa histórico
- APIs JSON para integração

---

## 🔗 URLs DE ACESSO

### Dashboard Principal
```
http://seu-site.com/financeiro/
```
**O quê?** Visão geral últimos 30 dias  
**Para quem?** Gerentes/Admins  
**Mostra:**
- Total de torneios
- Total de jogadores
- Faturamento bruto
- Rake cobrado
- Prêmios pagos
- Saldo do período

---

### Financeiro de Um Torneio Específico
```
http://seu-site.com/torneio/[ID]/financeiro/

Exemplo:
http://seu-site.com/torneio/1/financeiro/
http://seu-site.com/torneio/42/financeiro/
```

**O quê?** Detalhes completos de 1 torneio  
**Para quem?** Gerentes/Admins  
**Mostra:**
- Buy-ins recebidos
- Rake total
- Pote para prêmios
- Produtos vendidos (jackpot, etc)
- Prêmios pagos
- Saldo final

---

### Financeiro por Temporada
```
http://seu-site.com/financeiro/temporada/[SEASON_ID]/

Exemplo:
http://seu-site.com/financeiro/temporada/1/
```

**O quê?** Financeiro da temporada inteira  
**Para quem?** Gerentes  
**Mostra:**
- Todos os torneios da temporada
- Totais agregados
- Gráficos de evolução
- Comparativas com meses anteriores

---

### Financeiro com Filtro de Período
```
http://seu-site.com/financeiro/periodo/
```

**O quê?** Financeiro com filtro de datas customizado  
**Para quem?** Gerentes/Contadores  
**Como usar?**
1. Clique em "Financeiro" → "Por Período"
2. Selecione data início
3. Selecione data fim
4. Clique "Filtrar"

**Mostra:**
- Todos torneios no período
- Totais por tipo de torneio
- Comparativa com período anterior
- Gráficos

---

### Relatório Financeiro Completo (NOVO!)
```
http://seu-site.com/relatorio/financeiro/completo/
```

**O quê?** Relatório profissional com comparativas  
**Para quem?** Contadores/Finance Manager  
**Inclui:**
- Período atual vs anterior
- Variações percentuais
- Torneios por tipo
- Top 10 maiores torneios
- Fluxo de caixa
- Margens por torneio
- Exportação para Excel/PDF (em breve)

---

### Reconciliação de Um Torneio
```
http://seu-site.com/torneio/[ID]/financeiro/reconciliar/

Exemplo:
http://seu-site.com/torneio/1/financeiro/reconciliar/
```

**O quê?** Verificar saldo esperado vs real  
**Para quem?** Caixa/Admin  
**Para que?**
- Validar se todos os valores batem
- Detectar discrepâncias
- Gerar relatório de conferência

---

## 🎯 COMO NAVEGAR (Passo a Passo)

### Via Admin Panel
1. Login com conta admin
2. Clique em **"Financeiro"** (no menu lateral)
3. Escolha uma opção:
   - **Dashboard** → Visão geral
   - **Por Período** → Filtro de datas
   - **Por Torneio** → Específico (vem do torneio)

### Via URL Direta
- Copie/cola a URL acima no navegador
- Qualquer admin pode acessar

### Via Links nos Torneios
1. Vá para "Torneios"
2. Clique em um torneio
3. Procure por **"📊 Financeiro"** (botão azul)
4. Clique para ver detalhes

---

## 📊 O QUE VER EM CADA TELA

### DASHBOARD (/financeiro/)
```
┌─────────────────────────────────────┐
│ 📈 Relatório Financeiro - Últimos 30 dias
│
│ ┌──────────────┐  ┌──────────────┐
│ │ Faturamento  │  │ Rake Cobrado │
│ │   R$ 5.000   │  │    R$ 500    │
│ └──────────────┘  └──────────────┘
│
│ ┌──────────────┐  ┌──────────────┐
│ │ Pote Prêmios │  │ Prêmios Pagos│
│ │   R$ 4.500   │  │   R$ 4.200   │
│ └──────────────┘  └──────────────┘
│
│ Saldo: R$ 300 ✅
│
│ Torneios: 8
│ Jogadores: 45
└─────────────────────────────────────┘
```

### TORNEIO ESPECÍFICO (/torneio/1/financeiro/)
```
┌─────────────────────────────────────┐
│ Torneio: Aberto de Taubate #15
│ Data: 15/12/2025
│
│ ENTRADA (o que você cobrou)
│ ├─ Buy-in: R$ 100 × 12 = R$ 1.200
│ ├─ Rebuys: 2 × R$ 100 = R$ 200
│ ├─ Add-ons: 1 × R$ 100 = R$ 100
│ ├─ Produtos: Jackpot R$ 50
│ └─ TOTAL: R$ 1.550
│
│ CUSTOS (o que você pagou)
│ ├─ Rake: R$ 150
│ ├─ Prêmios: R$ 1.200
│ └─ TOTAL: R$ 1.350
│
│ SALDO: R$ 200 ✅
│ MARGEM: 12.9%
└─────────────────────────────────────┘
```

### PERÍODO (/financeiro/periodo/)
```
┌─────────────────────────────────────┐
│ Período: 01/12/2025 a 15/12/2025
│
│ COMPARATIVA
│ Período Atual   Período Anterior
│ 8 torneios      6 torneios      ↑ 33%
│ 45 jogadores    38 jogadores    ↑ 18%
│ R$ 5.000        R$ 3.500        ↑ 43%
│
│ RANKING TORNEIOS
│ 1. Aberto de Taubate    R$ 1.550
│ 2. Friday Night Poker   R$ 1.200
│ 3. Sat Night Special    R$ 800
│
│ GRÁFICO (faturamento por dia)
│ [Gráfico de linha]
└─────────────────────────────────────┘
```

---

## 🔐 PERMISSÕES

### Quem pode acessar?
- ✅ **Admin do clube** (acesso total)
- ✅ **Gerente financeiro** (se tiver flag is_staff)
- ❌ **Jogadores normais** (acesso negado)
- ❌ **Anônimos** (redireciona para login)

### Como dar acesso?
Se quiser que alguém acesse financeiro:

```python
# Via Django Shell
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='gerente@club.com')
user.is_staff = True  # Permite acessar admin
user.save()
```

---

## 📱 Dados que você vê

### Em QUALQUER tela financeira
```
Entrada (Receita):
├─ Buy-ins recebidos
├─ Rebuys
├─ Add-ons
├─ Produtos (jackpot, bounty, etc)
└─ TOTAL

Saída (Custos):
├─ Rake cobrado
├─ Prêmios pagos
└─ TOTAL

Resultado:
├─ Saldo (Entrada - Saída)
├─ Margem % (Rake / Entrada)
└─ Status ✅/⚠️
```

### Dinâmica
- Atualiza em **tempo real** (não precisa refresh)
- Cálculos automáticos (sem risco de erro manual)
- Conforme lança resultado, números mudam

---

## 🚀 RECURSOS AVANÇADOS

### API JSON (Para integração)
```
GET /api/financial/summary/
Retorna JSON com totais

Exemplo resposta:
{
  "periodo": "últimos 30 dias",
  "torneios": 8,
  "jogadores": 45,
  "faturamento": 5000.00,
  "rake": 500.00,
  "premios": 4200.00,
  "saldo": 300.00
}
```

### Reconciliação Automática
```
GET /torneio/1/financeiro/reconciliar/

Verifica:
- Valores esperados vs reais
- Discrepâncias
- Gera relatório de conferência
```

### Logs de Transações
Cada movimentação financeira fica registrada:
```
15/12/2025 14:30 - Lançou resultado (Fabiano terminou 1º: +R$ 500)
15/12/2025 14:25 - Novo inscrito (João, buy-in R$ 100)
15/12/2025 14:20 - Aberto de Taubate iniciado
```

---

## 📋 CHECKLIST - Como confirmar que tudo funciona

- [ ] Acesso `/financeiro/` mostra últimos 30 dias
- [ ] Clique em um torneio → financeiro dele aparece
- [ ] Filtro de período filtra corretamente
- [ ] Números batem com cálculos manuais
- [ ] Quando lança resultado, valores mudam
- [ ] Rake aparece corretamente
- [ ] Margem calcula certo
- [ ] Saldo está claro

---

## ⚠️ TROUBLESHOOTING

### "Erro 404 ao acessar /financeiro/"
**Solução:** Verifique se você é admin (is_staff=True)

### "Números não batem"
**Solução:** 
1. Verifique se todos resultados foram lançados
2. Confira rake configurado no torneio
3. Verifique se produtos foram marcados

### "Financeiro diferente de ontem"
**Normal!** Atualiza em tempo real. Se alguém editou um resultado, número muda.

### "Não consigo editar valores"
**Correto** - É apenas consulta (não permite edição direta por segurança)

---

## 🎯 PRÓXIMAS FEATURES (Roadmap)

- [ ] Exportar relatório para Excel
- [ ] Exportar para PDF
- [ ] Gráficos de evolução (mês a mês)
- [ ] Previsão de caixa
- [ ] Relatório de clientes (quem mais fatura)
- [ ] Análise de margens por tipo de torneio
- [ ] Integração com contabilidade
- [ ] Alertas de saldo baixo

---

## 📞 Dúvidas?

**Qual URL acessar?**
- Gerenciador geral: `/financeiro/`
- Um torneio: `/torneio/{ID}/financeiro/`
- Por período: `/financeiro/periodo/`
- Relatório: `/relatorio/financeiro/completo/`

**Por que valores diferentes?**
- Verifica se todos resultados foram lançados
- Alguns torneios podem estar ainda abertos

**Como aumentar margem?**
- Aumentar rake
- Reduzir prêmios
- Vender mais produtos (jackpot, bounty)

---

**Versão:** 1.0  
**Data:** 17/12/2025  
**Status:** Pronto para usar
