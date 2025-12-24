# ✏️ Google Cloud Console - Valores Exatos para Copiar/Colar

## 📋 RESUMO RÁPIDO

Este documento mostra EXATAMENTE o que você precisa digitar/colar em cada campo.

---

## 🆔 PASSO 2: Criar Projeto

### Campo: Project name
```
COPIE E COLE EXATAMENTE:

Poker Ranking
```

---

## 🔌 PASSO 3: Ativar API

### Buscar por:
```
DIGITE:

google+ api

(ou procure na lista por "Google+ API")
```

---

## 📝 PASSO 4: OAuth Consent Screen - App Information

### Campo 1: App name
```
COPIE E COLE:

Poker Ranking
```

### Campo 2: User support email
```
SEU EMAIL (exemplo):

seu.email@gmail.com
```

### Campo 3: Developer contact email
```
SEU EMAIL (mesmo de cima):

seu.email@gmail.com
```

---

## 🎫 PASSO 5: Create OAuth 2.0 Client ID

### Campo 1: Name
```
COPIE E COLE:

Poker Ranking Web Client
```

### Campo 2: Authorized JavaScript origins

**Clique em "+ Add URI" 2 VEZES e adicione:**

**URI #1:**
```
http://localhost:8000
```

**URI #2:**
```
http://127.0.0.1:8000
```

**Para produção depois, adicione também:**
```
https://seu-dominio-poker.com
```

---

### Campo 3: Authorized redirect URIs

**Clique em "+ Add URI" 2 VEZES e adicione:**

**URI #1 (CUIDADO COM A BARRA FINAL /):**
```
http://localhost:8000/accounts/google/login/callback/
```

**URI #2 (CUIDADO COM A BARRA FINAL /):**
```
http://127.0.0.1:8000/accounts/google/login/callback/
```

**Para produção depois, adicione também:**
```
https://seu-dominio-poker.com/accounts/google/login/callback/
```

---

## 🎁 RESULTADO FINAL

Após clicar [Create], você verá uma janela com:

### CLIENT ID (Copie tudo):
```
Exemplo:
1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com

Seu valor será diferente - COPIE TODO O TEXTO
```

### CLIENT SECRET (Copie tudo):
```
Exemplo:
GOCSPX-abcdefghijklmnopqrstuvwxyz123456

Seu valor será diferente - COPIE TODO O TEXTO
```

---

## 📝 Colando no Django Admin

Após copiar, vá para: `http://localhost:8000/admin`

### Campo: Provider
```
SELECIONE (dropdown):

Google
```

### Campo: Name
```
COPIE E COLE:

Google OAuth
```

### Campo: Client ID
```
COLE AQUI:

[Cole o Client ID que você copiou do Google Cloud Console]
```

### Campo: Secret key
```
COLE AQUI:

[Cole o Client Secret que você copiou do Google Cloud Console]
```

### Campo: Sites
```
SELECIONE:

localhost:8000 (ou seu site padrão)
```

---

## ⚠️ CUIDADOS IMPORTANTES

### ❌ ERROS COMUNS

1. **Esquecer a barra final (/) nas redirect URIs**
   ```
   ❌ ERRADO:
   http://localhost:8000/accounts/google/login/callback
   
   ✅ CORRETO:
   http://localhost:8000/accounts/google/login/callback/
   ```

2. **Colocar HTTPS em localhost**
   ```
   ❌ ERRADO:
   https://localhost:8000
   
   ✅ CORRETO:
   http://localhost:8000
   ```

3. **Espaços extras ao copiar Client ID ou Secret**
   ```
   ❌ ERRADO:
   1234567890-abc... [espaço]
   
   ✅ CORRETO:
   1234567890-abc...
   ```

4. **Confundir Client ID com Secret**
   - Client ID: número longo com `.apps.googleusercontent.com`
   - Client Secret: começa com `GOCSPX-`

---

## 📋 CHECKLIST DE DIGITAÇÃO

```
☐ Projeto criado com nome "Poker Ranking"
☐ Google+ API ativada
☐ OAuth Consent Screen criado (External)
☐ App name: "Poker Ranking"
☐ Emails preenchidos (seu email)
☐ Web Application selecionado
☐ Name: "Poker Ranking Web Client"
☐ JavaScript Origins adicionadas (2):
  ☐ http://localhost:8000
  ☐ http://127.0.0.1:8000
☐ Redirect URIs adicionadas (2):
  ☐ http://localhost:8000/accounts/google/login/callback/
  ☐ http://127.0.0.1:8000/accounts/google/login/callback/
☐ Client ID copiado (sem espaços)
☐ Client Secret copiado (sem espaços)
☐ Django Admin preenchido:
  ☐ Provider: Google
  ☐ Name: Google OAuth
  ☐ Client ID: [colado]
  ☐ Secret key: [colado]
  ☐ Site: selecionado
  ☐ Salvo
```

---

## 🧪 TESTAR

Após completar tudo:

1. Acesse: `http://localhost:8000/accounts/login/`
2. Clique em "Entrar com Google"
3. Se vir a tela de login do Google: ✅ FUNCIONANDO!
4. Faça login e autorize: ✅ SUCESSO!

---

## 🆘 SE ALGO DER ERRADO

### "Redirect URI mismatch"
→ Verifique se a URI está EXATAMENTE igual (com barra final!)

### "Invalid Client"
→ Verifique se Client ID está correto (sem espaços)

### "Invalid Client Secret"
→ Verifique se Secret está correto (sem espaços)

### "Credentials not found in Django"
→ Clique em [Save] após preencher tudo no Django Admin

### "Google+ API not enabled"
→ Volte e clique em [ENABLE] para Google+ API

---

## 🎯 DÚVIDAS RÁPIDAS

**P: Preciso de "External" ou "Internal"?**
A: External (permite qualquer Google Account)

**P: Qual projeto usar para produção?**
A: Crie um novo projeto quando for ao vivo

**P: Preciso de "Android" ou "iOS"?**
A: Não, use "Web application"

**P: Os valores mudam?**
A: Não, esses valores (Client ID/Secret) são fixos por projeto

**P: Posso regenerar?**
A: Sim, clique em [Regenerate Secret] se perder

---

## ✅ VOCÊ TERMINOU!

Parabéns! Agora você tem suas credenciais do Google prontas para usar! 🎉

Se tiver dúvidas, releia os documentos:
- `GOOGLE_CLOUD_CONSOLE_DETALHADO.md` - Explicação completa
- `GOOGLE_CLOUD_CONSOLE_VISUAL.md` - Screenshots em ASCII
- Este arquivo - Valores exatos para copiar/colar
