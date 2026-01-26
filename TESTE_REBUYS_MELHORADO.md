# 🧪 Guia de Teste - Sistema de Rebuys Melhorado

## Como Testar as Novas Funcionalidades

---

## 📋 Pré-requisitos para Teste

1. ✓ Banco de dados migrado (migration 0032 aplicada)
2. ✓ Servidor Django rodando
3. ✓ Admin logged in
4. ✓ Torneio com rebuys/addons configurados

---

## 🧪 Teste 1: Modal de Confirmação Aparece

### Passos:
1. Acesse página de inscrições de um torneio
2. Localize um jogador inscrito
3. Clique no botão de **REBUY** (ícone de seta para cima vermelha)

### Resultado Esperado:
✅ Modal com título "Confirmar Rebuy Simples" aparece  
✅ Modal mostra dados do jogador  
✅ Campo de observação está vazio e focado  
✅ Botões "Cancelar" e "Confirmar Lançamento" visíveis  

---

## 🧪 Teste 2: Observação é Salva

### Passos:
1. Clique em REBUY de um jogador
2. No campo de observação, digite: `Teste de observação 123`
3. Clique "Confirmar Lançamento"
4. Aguarde mensagem de sucesso

### Resultado Esperado:
✅ Modal fecha  
✅ Notificação "Rebuy adicionado! (1x)" aparece  
✅ Counter do jogador atualiza para 1  
✅ Observação foi salva no banco

### Como Verificar no Banco:
```python
# No Django Shell
python manage.py shell

from core.models import PlayerProductPurchase
compra = PlayerProductPurchase.objects.latest('id')
print(compra.observacao)
# Deve imprimir: "Teste de observação 123"
```

---

## 🧪 Teste 3: Cancelamento Funciona

### Passos:
1. Clique em REBUY de um jogador diferente
2. Adicione uma observação
3. Clique "Cancelar"

### Resultado Esperado:
✅ Modal fecha  
✅ Nenhuma notificação aparece  
✅ Contador do jogador NÃO muda  
✅ Nenhum lançamento é feito  

---

## 🧪 Teste 4: Rebuy Duplo Funciona

### Passos:
1. Clique em REBUY DUPLO (dois ícones de seta)
2. Adicione observação: `Rebuy duplo confirmado`
3. Confirme

### Resultado Esperado:
✅ Modal mostra "Rebuy Duplo"  
✅ Descrição mostra "Rebuy duplo (2x ou valor diferenciado)"  
✅ Valor correto é exibido  
✅ Counter de rebuy duplo atualiza  

---

## 🧪 Teste 5: Add-on Máximo 1

### Passos:
1. Clique em ADD-ON de um jogador
2. Adicione observação: `Primeiro addon`
3. Confirme
4. Tente clicar em ADD-ON novamente no mesmo jogador

### Resultado Esperado:
✅ Primeiro add-on: Lançado com sucesso  
✅ Segundo add-on: Aparece erro "máximo 1 permitido"  
✅ Counter mostra 1 (não incrementa)  

---

## 🧪 Teste 6: Dados Corretos no Modal

### Passos:
1. Clique em REBUY de qualquer jogador
2. Observar modal

### Resultado Esperado:
✅ Nome do jogador está correto  
✅ Tipo mostra corretamente (Rebuy Simples, Duplo, Add-on)  
✅ Valor está formatado em R$ (ex: R$ 100,00)  
✅ Quantidade atual mostra número correto  
✅ Todos os dados batem com configuração do torneio  

---

## 🧪 Teste 7: Notificações Aparecem

### Passos:
1. Clique REBUY + Confirme (sucesso esperado)
2. Observe notificação

### Resultado Esperado:
✅ Notificação verde com checkmark  
✅ Mensagem: "Rebuy adicionado! (2x)"  
✅ Desaparece automaticamente após alguns segundos  

### Para Erro:
1. Configure rebuy como "não permitido" no torneio
2. Tente lançar rebuy
3. Clique confirmar

### Resultado Esperado:
✅ Notificação vermelha com warning  
✅ Mensagem: "Rebuy não permitido neste torneio"  
✅ Counter não muda  

---

## 🧪 Teste 8: Verificar no Admin Django

### Passos:
1. Acesse Django Admin: `/admin/core/playerproductpurchase/`
2. Procure por uma compra recém criada
3. Clique para editar

### Resultado Esperado:
✅ Campo "observacao" está presente  
✅ Valor salvo é exibido  
✅ Data de lançamento está correta  
✅ Usuário que lançou está registrado  

---

## 📊 Teste de Dados - Query SQL

```sql
-- Ver todas as observações de rebuys
SELECT 
    player.nome,
    product.nome,
    purchase.quantidade,
    purchase.observacao,
    auth_user.username as lancado_por,
    purchase.data_lancamento
FROM core_playerproductpurchase purchase
JOIN core_player player ON purchase.player_id = player.id
JOIN core_tournamentproduct product ON purchase.product_id = product.id
LEFT JOIN auth_user ON purchase.lancado_por_id = auth_user.id
ORDER BY purchase.data_lancamento DESC
LIMIT 10;
```

---

## 🐛 Possíveis Problemas e Soluções

### Problema: Modal não aparece
**Solução:**
- Verifique se Bootstrap JS está carregado
- Veja console (F12) para erros JavaScript
- Verifique se template foi atualizado

### Problema: Observação não salva
**Solução:**
- Confirme que migration foi aplicada (`python manage.py migrate`)
- Verifique se o campo aparece no model
- Veja logs do servidor para erros

### Problema: Modal abre mas botão não funciona
**Solução:**
- Verifique CSRF token está presente
- Veja console para erros AJAX
- Confirme que view foi atualizada

### Problema: Contador não atualiza
**Solução:**
- Refresque a página
- Verifique classe CSS do counter
- Veja resposta JSON da API

---

## ✅ Checklist de Teste Completo

- [ ] Modal abre ao clicar em rebuy
- [ ] Campo de observação está vazio e funcional
- [ ] Dados do jogador são exibidos corretamente
- [ ] Valor está formatado corretamente
- [ ] Botão "Cancelar" fecha modal sem fazer nada
- [ ] Botão "Confirmar" lança o rebuy
- [ ] Observação é salva no banco
- [ ] Counter atualiza após lançamento
- [ ] Notificação de sucesso aparece
- [ ] Add-on limita a máximo 1
- [ ] Rebuy duplo funciona corretamente
- [ ] Admin vê observação quando edita no Django Admin
- [ ] Observação aparece em relatórios

---

## 📝 Logs Esperados

Ao lançar um rebuy, você deve ver no console do servidor:

```
[13/Jan/2026 14:30:45] "POST /api/torneio/123/rebuy-addon/ HTTP/1.1" 200 125
```

E na resposta JSON:
```json
{
    "success": true,
    "message": "Rebuy adicionado! (1x)",
    "quantidade": 1,
    "valor_total": "100.00"
}
```

---

## 🎯 Cenários de Teste Recomendados

1. **Teste Feliz**: Lançar rebuy com observação → Deve funcionar
2. **Teste de Erro**: Lançar add-on 2x → Deve bloquear
3. **Teste de Cancelamento**: Abrir modal e cancelar → Não deve lançar
4. **Teste de Múltiplos**: Lançar 5 rebuys em sequência → Todos devem contar
5. **Teste de Observações**: Lançar 3 rebuys com observações diferentes → Devem ser distintas

---

## 🚀 Próximo Passo

Após confirmar que tudo funciona:
1. Teste em produção
2. Treine admins sobre nova interface
3. Monitore observações adicionadas
4. Use dados para melhorias futuras

---

**Data de Criação**: 13 de Janeiro de 2026  
**Última Atualização**: 13 de Janeiro de 2026
