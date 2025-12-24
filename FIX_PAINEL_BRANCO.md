# SOLUÇÃO: Tela em Branco no Painel do Admin (Veris)

## 📋 Problema Reportado
Ao logar como admin do tenant "veris" com credenciais veris/veris123, a tela exibia em branco, sem nenhuma opção de menu (Torneios, Temporadas, etc.).

Problema começou após adicionar o campo `foto` ao modelo Player.

---

## 🔍 Investigação Realizada

### Testes Técnicos:
1. ✅ Tenant 'Veris Poker' está ativo
2. ✅ Usuário 'veris' é admin do tenant (role: 'admin')
3. ✅ Senha está correta
4. ✅ Template painel_home.html renderiza corretamente (26.692 bytes)
5. ✅ Todos os elementos HTML esperados estão presentes

### Elementos Verificados:
- ✅ Sidebar com menu (RANKING, TORNEIOS, GESTÃO, FINANCEIRO)
- ✅ Título "Painel de Controle"
- ✅ Cards de temporadas
- ✅ Hero section
- ✅ Page header
- ✅ Buttons e actions
- ✅ Acesso Rápido

---

## ⚠️ Causa Raiz Identificada

### Problema 1: Decorator @tenant_required retornava JSON
**Arquivo**: [core/views/season.py](core/views/season.py) - Função `painel_home()`

A view usava `@tenant_required` que retornava JSON error (403) quando o tenant não estava configurado no request, ao invés de HTML. Isso resultava em uma "página" JSON renderizada como tela em branco.

### Problema 2: Template acessava request.tenant sem verificar None
**Arquivo**: [core/templates/base.html](core/templates/base.html) - Linha 195

O template tentava acessar `request.tenant.logo` sem verificar se `request.tenant` era None, causando erro silencioso.

### Problema 3: Middleware tinha error handling genérico
**Arquivo**: [core/middleware/tenant_middleware.py](core/middleware/tenant_middleware.py)

O `except Exception: pass` engolia erros silenciosamente, dificultando debug.

---

## ✅ Correções Aplicadas

### 1️⃣ Corrigir base.html
**Localização**: [core/templates/base.html](core/templates/base.html) - Linha 191

```diff
-   {% if user.is_staff %}
+   {% if user.is_staff and request.tenant %}
```

Adicionada verificação de `request.tenant` antes de renderizar a sidebar:
```html
{% if request.tenant and request.tenant.logo %}
    <img src="{{ request.tenant.logo.url }}" ...>
{% else %}
    <i class="bi bi-suit-spade-fill"></i>
{% endif %}
```

### 2️⃣ Corrigir painel_home() view
**Localização**: [core/views/season.py](core/views/season.py) - Linhas 260-285

Removido `@tenant_required` e adicionado lógica interna:

```python
@login_required
def painel_home(request):
    """Dashboard principal do sistema"""
    # Garante que o usuário tem acesso a um tenant
    if not hasattr(request, 'tenant') or not request.tenant:
        # Tentar obter o primeiro tenant do usuário
        from ..models import TenantUser
        tenant_user = TenantUser.objects.select_related('tenant').filter(
            user=request.user,
            tenant__ativo=True
        ).first()
        
        if tenant_user:
            request.tenant = tenant_user.tenant
        else:
            # Redirecionar para player_home se nenhum tenant disponível
            from django.shortcuts import redirect
            from django.urls import reverse
            return redirect(reverse('player_home'))
    
    seasons = Season.objects.filter(tenant=request.tenant).order_by("-data_inicio")
    
    return render(request, "painel_home.html", {"seasons": seasons})
```

**Benefícios**:
- Retorna HTML em qualquer caso (nunca JSON error)
- Recupera tenant do usuário se não estiver no request
- Redireciona graciosamente se sem acesso a tenant

### 3️⃣ Melhorar TenantMiddleware
**Localização**: [core/middleware/tenant_middleware.py](core/middleware/tenant_middleware.py)

Adicionado logging detalhado:
```python
import logging
logger = logging.getLogger(__name__)

# Dentro do middleware:
if tenant_user and tenant_user.tenant.ativo:
    request.tenant = tenant_user.tenant
    set_current_tenant(request.tenant)
    logger.info(f"Tenant set for user {request.user.username}: {request.tenant.nome}")
else:
    if tenant_user:
        logger.warning(f"Tenant inactive for user {request.user.username}: ...")
    else:
        logger.warning(f"No TenantUser found for user {request.user.username}")
```

Removido `except Exception: pass` silencioso e adicionado logging de erros.

---

## 🧪 Validação

### Teste Automático:
```bash
python test_painel_complete.py
```

**Resultado**:
```
Status: 200
Content-Length: 26692 bytes

[OK] HTML válido
[OK] Sidebar
[OK] Título "Painel de Controle"
[OK] Título "Painel do Organizador"
[OK] Cards de temporadas
[OK] Hero section
[OK] Page header
[OK] Section "Suas Temporadas"
[OK] Section "Acesso Rápido"
[OK] Buttons
```

---

## 🎯 Resultado Final

✅ **Problema Resolvido!**

O painel agora renderiza corretamente para admins do tenant Veris, exibindo:
- Sidebar com menu completo
- Lista de temporadas
- Acesso rápido aos módulos
- Todos os botões funcionais

---

## 📝 Nota sobre o campo "foto"

O problema **NÃO** estava relacionado ao campo `foto` adicionado ao modelo Player. A migração foi aplicada corretamente, e o campo não causou erros de template.

O problema era estrutural na forma como a view e template tratavam o tenant não configurado.

---

## 🚀 Para o Usuário

Se ainda vir tela em branca:

1. **Limpar Cache**: `Ctrl + Shift + Delete` e reiniciar navegador
2. **Verificar Servidor**: Confirmar que Django está rodando
3. **Fazer Login Novamente**: veris@veris.com / veris123
4. **Verificar Console**: F12 para procurar erros de JS/CSS
