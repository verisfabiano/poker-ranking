# 🧪 TESTING GUIDE - PHASE 1 AUTHENTICATION HARDENING

## ✅ Quick Verification Checklist

### Django System
```bash
cd c:\projetos\poker_ranking
.\venv\Scripts\python.exe manage.py check
# Expected: "System check identified no issues (0 silenced)."
```

---

## 🧪 TESTES FUNCIONAIS

### 1️⃣ Rate Limiting Test

**Objetivo:** Verificar se rate limiting funciona

**Passos:**
1. Abrir browser em: `http://localhost:8000/auth/player-login/`
2. Tentar login 5 vezes com credenciais erradas
3. Na 6ª tentativa, deve receber HTTP 429
4. Aguardar 60 segundos e tentar novamente (deve funcionar)

**Esperado:**
```
❌ Status 200 - Login falhou (credenciais inválidas) - Tentativa 1-5
❌ Status 429 - Too Many Requests - Tentativa 6
✅ Status 200 - Login falhou (após esperar 60s)
```

---

### 2️⃣ Email Verification Test

**Objetivo:** Testar fluxo de verificação de email

**Passos:**
1. Abrir: `http://localhost:8000/auth/player-register/`
2. Preencher:
   - Nome: "Teste Email"
   - Email: "teste@ejemplo.com"
   - Senha: "SenhaForte123!"
   - Confirmação: "SenhaForte123!"
3. Clicar "Cadastrar"

**Esperado:**
```
✅ Redirecionado para "email_verification_pending.html"
✅ Mensagem: "Verifique seu email"
✅ Email enviado (check email backend)
```

**Continuação (sem email real):**
1. Abrir Django admin
2. Navegar para EmailVerificationToken
3. Copiar um token
4. Acessar: `http://localhost:8000/auth/verify-email/<token>/`

**Esperado:**
```
✅ Página de sucesso: "Email Verificado!"
✅ user.is_active agora = True
✅ Login agora funciona
```

---

### 3️⃣ Password Reset Test

**Objetivo:** Testar recuperação de senha

**Passos:**
1. Abrir: `http://localhost:8000/auth/forgot-password/`
2. Digite email registrado
3. Clicar "Enviar Link"

**Esperado:**
```
✅ Redirecionado para sucesso
✅ Mensagem genérica (não revela se email existe)
✅ Email enviado (check backend)
```

**Continuação:**
1. Abrir Django admin
2. Copiar PasswordResetToken
3. Acessar: `http://localhost:8000/auth/reset-password/<token>/`
4. Digite nova senha: "NovaSenha123!"
5. Confirmação: "NovaSenha123!"
6. Clicar "Salvar"

**Esperado:**
```
✅ Página de sucesso
✅ user.password atualizado (hashed)
✅ Login com nova senha funciona
❌ Mesmo token não funciona 2x (one-time use)
```

---

### 4️⃣ Form Simplification Test

**Objetivo:** Verificar que form está simplificado

**Passos:**
1. Abrir: `http://localhost:8000/auth/player-register-public/`
2. Inspecionar form

**Esperado:**
```
✅ Apenas 4 campos visíveis:
   - Nome
   - Email
   - Password
   - Password Confirmation
❌ NÃO deve ter: apelido, telefone
```

---

### 5️⃣ Username Auto-Generation Test

**Objetivo:** Verificar que username é gerado automaticamente

**Passos:**
1. Registre novo usuário (em local)
2. Abrir Django admin > User
3. Procurar usuário registrado

**Esperado:**
```
✅ Username: "player_xxxxxxxx" (16 caracteres)
✅ Username diferente para cada usuário
✅ Email diferente (pode reutilizar email)
```

---

### 6️⃣ Multi-tenant Hardening Test

**Objetivo:** Verificar que audit logging funciona

**Passos:**
1. Registre e faça login com um usuário
2. Abrir Django admin > TenantAuditLog

**Esperado:**
```
✅ Registro LOGIN criado
✅ user: <seu usuário>
✅ action: LOGIN
✅ ip_address: 127.0.0.1
✅ user_agent: <seu browser>
✅ success: True
```

**Teste Falha:**
1. Tentar login com email errado
2. Abrir Django admin > TenantAuditLog

**Esperado:**
```
✅ Registro LOGIN_FAILED criado
✅ success: False
✅ error_message: preenchido
✅ ip_address: 127.0.0.1
```

---

### 7️⃣ Templates Unification Test

**Objetivo:** Verificar que templates têm design consistente

**Passos:**
1. Navegar para diferentes páginas auth:
   - `/auth/player-login/`
   - `/auth/player-register/`
   - `/auth/forgot-password/`

**Esperado:**
```
✅ Mesmo header (base_auth.html)
✅ Mesma paleta de cores
✅ Mesma tipografia
✅ Mesmos spacing/padding
✅ Ícones Font Awesome visíveis
✅ Botões com gradiente (hover effect)
✅ Alertas com padrão visual consistente
```

**Mobile Test:**
1. Abrir DevTools (F12)
2. Toggle device toolbar (375px - iPhone SE)
3. Navegar páginas auth

**Esperado:**
```
✅ Layout responsivo (não horizontal scroll)
✅ Botões clicáveis (touch-friendly)
✅ Font size 16px (no zoom iOS)
✅ Spacing adequado
✅ Stack vertical (cards não lado a lado)
```

---

### 8️⃣ Dark Mode Test

**Objetivo:** Verificar que dark mode funciona

**Passos:**
1. System Preferences (Windows) > Display > Dark mode
2. Recarregar página

**Esperado:**
```
✅ Background escuro
✅ Cards com tema escuro
✅ Texto legível
✅ Sem contrast issues
```

---

## 📋 SECURITY VERIFICATION

### Rate Limiting
```bash
# Verificar decorator aplicado
grep -n "@rate_limit" core/views/*.py
# Esperado: 3 ocorrências (player_login, login_view, player_login_club)
```

### Email Tokens
```bash
# Verificar models
grep -n "class EmailVerificationToken" core/models.py
grep -n "class PasswordResetToken" core/models.py
# Esperado: ambos presentes
```

### Audit Logging
```bash
# Verificar model
grep -n "class TenantAuditLog" core/models.py
# Esperado: presente com 10+ ações
```

### Templates
```bash
# Contar templates criados
ls -la core/templates/auth/
# Esperado: 13+ arquivos .html
```

---

## 🔐 SECURITY TESTS

### Token Expiration
```bash
# Email token deve expirar em 24h
# Password token deve expirar em 2h
# Testar em Django shell:
from core.models import EmailVerificationToken
token = EmailVerificationToken.objects.first()
token.is_expired()  # Deve retornar False (acabou de criar)
```

### One-Time Use Prevention
```bash
# Um token não pode ser usado 2x
# Após usar um reset password token:
token.used_at  # Deve ter valor
token.mark_as_used()  # Não deve quebrar (idempotent)
```

### IP Tracking
```bash
# Verificar que IP está sendo registrado
from core.models import TenantAuditLog
log = TenantAuditLog.objects.filter(action='LOGIN').first()
log.ip_address  # Deve ser 127.0.0.1 em local
```

---

## 📊 PERFORMANCE TESTS

### Rate Limiting Performance
```bash
# Cache-based, deve ser < 1ms por check
# Use Django debug toolbar para verificar queries
```

### Email Service Performance
```bash
# Envio de email deve ser < 500ms (com SMTP)
# Ou async job se quiser
```

### Database Queries
```bash
# Verificar número de queries:
from django.db import connection
from django.test.utils import override_settings

# Deve ser minimal (1-2 queries por requisição)
```

---

## 🎯 CHECKLISTS POR RECURSO

### ✅ Rate Limiting
- [ ] Login recebe HTTP 429 após 5 tentativas
- [ ] IP é rastreado corretamente
- [ ] Timer de 60 segundos funciona
- [ ] Usuários diferentes têm limites separados

### ✅ Email Verification
- [ ] Email é enviado após registro
- [ ] Link no email funciona
- [ ] Token expira após 24h
- [ ] Não pode reutilizar token
- [ ] User ativado após verificação

### ✅ Password Reset
- [ ] Link é enviado para email registrado
- [ ] Link expira após 2h
- [ ] Link não pode ser reutilizado
- [ ] Nova senha funciona
- [ ] Email genérico (não revela se email existe)

### ✅ Forms
- [ ] Apenas 4 campos no form
- [ ] Validação de email
- [ ] Password min 8 caracteres
- [ ] Feedback visual de erro

### ✅ Username
- [ ] Username único (player_XXXXXXXX)
- [ ] Email pode ser reutilizado
- [ ] Username não muda

### ✅ Multi-tenant
- [ ] TenantAuditLog registra logins
- [ ] IP é salvo
- [ ] User agent é salvo
- [ ] Success/failure é rastreado

### ✅ Templates
- [ ] Design consistente
- [ ] Responsive em mobile
- [ ] Dark mode funciona
- [ ] Icons visíveis
- [ ] Sem erros de renderização

---

## 🚀 DEPLOYMENT CHECKLIST

Antes de ir para produção:

- [ ] Email SMTP configurado
- [ ] Testes passam localmente
- [ ] Rate limiting ajustado (se necessário)
- [ ] Tokens timeout verificados
- [ ] Audit log está funcionando
- [ ] Migrations foram rodadas
- [ ] Statics foram coletados
- [ ] Debug = False em produção
- [ ] ALLOWED_HOSTS configurado
- [ ] Email domain verificado

---

## 📝 NOTAS

1. **Local Testing:** Use console email backend (dev)
2. **Staging:** Use real SMTP
3. **Monitoring:** Setup TenantAuditLog alerts
4. **Performance:** Monitor cache hits
5. **User Feedback:** Recolher métricas de signup

---

**Test Version:** Phase 1 Complete  
**Last Updated:** 2024  
**Status:** Ready for Testing & Deployment
