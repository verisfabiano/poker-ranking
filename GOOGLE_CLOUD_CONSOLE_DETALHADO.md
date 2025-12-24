# 📱 Google Cloud Console - Guia Detalhado Passo a Passo

## 🎯 Objetivo Final

Obter **Client ID** e **Client Secret** para usar no seu Poker Ranking com Google OAuth.

---

## 📍 PASSO 1: Acessar Google Cloud Console

### 1.1 Abrir o Console

**URL:** https://console.cloud.google.com

```
Clique neste link ou copie/cole no navegador:
https://console.cloud.google.com
```

### 1.2 Login

- Se não tiver conta Google, crie uma
- Se tiver, faça login com sua conta Google

**Resultado esperado:**
```
┌─────────────────────────────────────────┐
│  Google Cloud Console                   │
│                                         │
│  [Seu nome] ▼                           │
│                                         │
│  Dashboard                              │
│  APIs & Services                        │
│  Projects                               │
│  ...                                    │
└─────────────────────────────────────────┘
```

---

## 🏗️ PASSO 2: Criar Novo Projeto

### 2.1 Localizar o Seletor de Projetos

```
┌──────────────────────────────────────────────────┐
│  ☰  Google Cloud              [Seu Nome] ▼      │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │ My First Project         ▼ (ou similar)  │ │
│  │                                            │ │
│  │ Clique aqui para trocar/criar projeto   │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

**Localização:** 
- Topo esquerdo da página
- Mostra o projeto atual
- Tem um dropdown com ▼

### 2.2 Clicar em "NEW PROJECT"

Após clicar no seletor:

```
┌─────────────────────────────────────────┐
│  Select a Project                       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ My First Project (ou similar)   │   │
│  │ Your projects                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ [+ NEW PROJECT]  ← CLIQUE AQUI  │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### 2.3 Preencher Dados do Novo Projeto

Uma janela vai abrir:

```
┌─────────────────────────────────────────────────┐
│  Create a Project                               │
│                                                 │
│  Project name:                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Poker Ranking                            │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Organization: (deixe como está)                │
│  Folder: (deixe como está)                      │
│                                                 │
│  [Create]  [Cancel]                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Preenchimento:**
1. **Project name:** Digite `Poker Ranking`
2. **Organization:** Deixe padrão
3. Clique em **[Create]**

### 2.4 Aguardar Criação

```
Criando projeto...
[████████████████████] 30%

Isso leva alguns segundos
```

**Resultado:** Você será redirecionado para o dashboard do novo projeto

---

## 🔌 PASSO 3: Ativar Google+ API

### 3.1 Encontrar o Buscador de APIs

```
┌──────────────────────────────────────────────────┐
│  Google Cloud                      [Seu Nome] ▼  │
│  Poker Ranking (seu projeto)                     │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │ 🔍 Search for APIs and Services            │ │ ← AQUI
│  └────────────────────────────────────────────┘ │
│                                                   │
│  Recommended APIs:                               │
│  ...                                             │
└──────────────────────────────────────────────────┘
```

### 3.2 Buscar Google+ API

Clique na barra de busca e digite:

```
[🔍                                    ]
```

Digite: `google+ api`

### 3.3 Selecionar "Google+ API"

Resultado da busca:

```
┌──────────────────────────────────────┐
│ Search Results                       │
│                                      │
│ 📊 Google+ API                    │ │ ← CLIQUE
│    Social API for Google+         │ │
│                                      │
│ 📊 Google+ Sign-in API            │ │
│    (deprecated)                   │ │
│                                      │
└──────────────────────────────────────┘
```

Clique em **Google+ API** (primeira opção)

### 3.4 Ativar a API

```
┌────────────────────────────────────────────┐
│  Google+ API                               │
│                                            │
│  Social API for Google+                    │
│                                            │
│  [ENABLE]  ← CLIQUE AQUI                   │
│                                            │
└────────────────────────────────────────────┘
```

Uma tela de carregamento vai aparecer:

```
Activating Google+ API...
[████████████████████] 50%

Isso leva uns 20-30 segundos
```

**Resultado:** Mensagem "Google+ API is now enabled"

---

## 🔑 PASSO 4: Criar OAuth Consent Screen

### 4.1 Ir para OAuth Consent Screen

Na barra lateral esquerda, procure:

```
LEFT SIDEBAR:
├── Dashboard
├── Enabled APIs
├── OAuth Consent Screen  ← CLIQUE AQUI
├── Credentials
├── Quotas
└── ...
```

**Localização:** 
- Menu esquerdo → "APIs & Services" → "OAuth Consent Screen"

### 4.2 Selecionar "External"

```
┌────────────────────────────────────┐
│  OAuth Consent Screen              │
│                                    │
│  User Type                         │
│                                    │
│  ○ Internal                        │
│  ● External  ← SELECIONE ESTA      │
│                                    │
│  [Create]                          │
│                                    │
└────────────────────────────────────┘
```

Selecione **External** e clique **[Create]**

### 4.3 Preencher App Information

Uma forma grande vai abrir:

```
┌──────────────────────────────────────────────┐
│  OAuth Consent Screen - Create                │
│                                              │
│  * App name:                                  │
│  ┌──────────────────────────────────────┐   │
│  │ Poker Ranking                        │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  * User support email:                       │
│  ┌──────────────────────────────────────┐   │
│  │ seu@email.com                        │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Developer contact information:              │
│  * Email address:                            │
│  ┌──────────────────────────────────────┐   │
│  │ seu@email.com                        │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  [Save and Continue]  [Back]  [Cancel]      │
│                                              │
└──────────────────────────────────────────────┘
```

**Preenchimento:**
1. **App name:** `Poker Ranking`
2. **User support email:** `seu@email.com` (sua email)
3. **Developer contact email:** `seu@email.com` (sua email)
4. Clique **[Save and Continue]**

### 4.4 Próximas Telas (Skip)

Você verá mais telas:
- "Scopes" → Click **[Save and Continue]**
- "Test users" → Click **[Save and Continue]**
- "Summary" → Click **[Back to Dashboard]** or **[Save and Continue]**

**Resultado:** OAuth Consent Screen configurada ✅

---

## 🎫 PASSO 5: Criar OAuth 2.0 Credentials

### 5.1 Ir para Credentials

No menu lateral:

```
LEFT SIDEBAR:
├── Dashboard
├── OAuth Consent Screen  (acabamos de fazer)
├── Credentials  ← CLIQUE AQUI
├── Quotas
└── ...
```

### 5.2 Clicar em "Create Credentials"

```
┌────────────────────────────────────┐
│  Credentials                       │
│                                    │
│  [+ Create Credentials]  ← CLIQUE  │
│                                    │
│  No credentials yet                │
│  Create a credential to get started│
│                                    │
└────────────────────────────────────┘
```

Clique em **[+ Create Credentials]**

Um dropdown vai aparecer:

```
┌──────────────────────────────────┐
│ Create Credentials               │
│                                  │
│ ✓ OAuth client ID  ← SELECIONE   │
│ ✓ API Key                        │
│ ✓ Service Account                │
│ ✓ Application Default Credentials│
│                                  │
└──────────────────────────────────┘
```

Clique em **"OAuth client ID"**

### 5.3 Selecionar Application Type

```
┌─────────────────────────────────────┐
│  Create OAuth 2.0 Client IDs        │
│                                     │
│  You must first configure the       │
│  OAuth consent screen               │
│                                     │
│  [Go to OAuth Consent Screen]       │
│                                     │
│  OU                                 │
│                                     │
│  Application type:                  │
│                                     │
│  ○ Web application  ← SELECIONE     │
│  ○ Desktop app                      │
│  ○ Installed application            │
│  ○ Android                          │
│  ○ iOS                              │
│  ○ Chrome extension                 │
│                                     │
│  [Create]                           │
│                                     │
└─────────────────────────────────────┘
```

**Seleção:**
1. Escolha **"Web application"**
2. Clique **[Create]**

### 5.4 Preencher Detalhes da Aplicação Web

```
┌──────────────────────────────────────────────┐
│  Create OAuth 2.0 Client ID                  │
│                                              │
│  Name: (nome da credencial)                  │
│  ┌──────────────────────────────────────┐   │
│  │ Poker Ranking Web Client             │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Authorized JavaScript origins:              │
│  (URLs onde sua app está hospedada)          │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │ + Add URI                            │   │ ← CLIQUE
│  └──────────────────────────────────────┘   │
│                                              │
│  Authorized redirect URIs:                   │
│  (URLs para Google redirecionar depois OAuth)│
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │ + Add URI                            │   │ ← CLIQUE
│  └──────────────────────────────────────┘   │
│                                              │
│  [Create]  [Cancel]                         │
│                                              │
└──────────────────────────────────────────────┘
```

### 5.5 Adicionar JavaScript Origins

Clique no primeiro **"+ Add URI"** e adicione:

```
Para DESENVOLVIMENTO (localhost):
1. http://localhost:8000
2. http://127.0.0.1:8000

Para PRODUÇÃO (depois):
3. https://seu-poker-ranking.com
4. https://www.seu-poker-ranking.com
```

**Como adicionar:**
```
┌──────────────────────────────┐
│ URIs                         │
│                              │
│ [http://localhost:8000    ] ✗ │
│ [http://127.0.0.1:8000    ] ✗ │
│ [https://seu-dominio.com  ] ✗ │
│                              │
│ [+ Add another]              │
│                              │
└──────────────────────────────┘
```

Clique **"+ Add another"** para adicionar mais

### 5.6 Adicionar Redirect URIs

Clique no segundo **"+ Add URI"** e adicione:

```
Para DESENVOLVIMENTO (localhost):
1. http://localhost:8000/accounts/google/login/callback/
2. http://127.0.0.1:8000/accounts/google/login/callback/

Para PRODUÇÃO (depois):
3. https://seu-poker-ranking.com/accounts/google/login/callback/
4. https://www.seu-poker-ranking.com/accounts/google/login/callback/
```

⚠️ **IMPORTANTE:** Incluir o `/` final!

```
┌────────────────────────────────────────────────┐
│ Authorized redirect URIs                       │
│                                                │
│ [http://localhost:8000/accounts/google/    ] ✗ │
│  login/callback/                              │
│                                                │
│ [http://127.0.0.1:8000/accounts/google/    ] ✗ │
│  login/callback/                              │
│                                                │
│ [https://seu-dominio.com/accounts/google/  ] ✗ │
│  login/callback/                              │
│                                                │
│ [+ Add another]                               │
│                                                │
└────────────────────────────────────────────────┘
```

### 5.7 Criar e Copiar Credenciais

Clique **[Create]**

```
┌─────────────────────────────────────────────┐
│  OAuth 2.0 Client Created                   │
│                                             │
│  Your Client ID:                            │
│  ┌──────────────────────────────────────┐  │
│  │ 1234567890-abc...                    │  │
│  │                                       │  │  ← COPIE ISTO
│  │ [Copy to clipboard]                  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Your Client Secret:                        │
│  ┌──────────────────────────────────────┐  │
│  │ GOCSPX-xyz...                        │  │
│  │                                       │  │  ← COPIE ISTO
│  │ [Copy to clipboard]                  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  [Download JSON]                            │
│  [OK]                                       │
│                                             │
└─────────────────────────────────────────────┘
```

**COPIE:**
1. **Client ID** (número longo)
2. **Client Secret** (começa com GOCSPX-)

⚠️ **GUARDE COM SEGURANÇA!** Não compartilhe!

---

## ✅ PASSO 6: Verificar Credenciais

De volta na tela de Credentials:

```
┌─────────────────────────────────────┐
│  Credentials                        │
│                                     │
│  OAuth 2.0 Client IDs               │
│  ┌─────────────────────────────────┐│
│  │ Name: Poker Ranking Web Client  ││
│  │ Client ID: 1234567890-abc...    ││
│  │ Type: Web application            ││
│  └─────────────────────────────────┘│
│                                     │
│  [Click para editar]                │
│                                     │
└─────────────────────────────────────┘
```

✅ Credenciais criadas com sucesso!

---

## 📊 RESUMO DO QUE FOI FEITO NO GOOGLE CLOUD

```
┌──────────────────────────────────────────────┐
│  CHECKLIST GOOGLE CLOUD CONSOLE              │
├──────────────────────────────────────────────┤
│ ✅ Criar Projeto: "Poker Ranking"            │
│ ✅ Ativar: Google+ API                       │
│ ✅ Criar: OAuth Consent Screen (External)    │
│ ✅ Configurar: App Information               │
│ ✅ Criar: OAuth 2.0 Client ID                │
│ ✅ Selecionar: Web Application               │
│ ✅ Adicionar: JavaScript Origins             │
│    - http://localhost:8000                   │
│    - http://127.0.0.1:8000                   │
│ ✅ Adicionar: Redirect URIs                  │
│    - http://localhost:8000/accounts/...     │
│    - http://127.0.0.1:8000/accounts/...     │
│ ✅ Copiar: Client ID                         │
│ ✅ Copiar: Client Secret                     │
└──────────────────────────────────────────────┘
```

---

## 🎁 RESULTADO FINAL

Você agora tem:

```
CLIENT ID:
1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com

CLIENT SECRET:
GOCSPX-abcdefghijklmnopqrstuvwxyz123456
```

---

## 📋 PRÓXIMO PASSO: Adicionar no Django

Com estas credenciais, você pode:

### Opção 1: Django Admin
```
1. http://localhost:8000/admin
2. Social Applications → Add
3. Provider: Google
4. Cole Client ID e Secret
5. Save
```

### Opção 2: Script Python
```bash
python setup_google_oauth.py "seu_client_id" "seu_client_secret"
```

---

## 🆘 PROBLEMAS COMUNS

### Problema: "You haven't configured OAuth Consent Screen"
**Solução:** Volte ao PASSO 4 e crie o OAuth Consent Screen primeiro

### Problema: "Redirect URI mismatch"
**Solução:** Verifique se as URIs no Google Console são exatamente iguais (com trailing slash!)

### Problema: "Invalid Client ID"
**Solução:** Certifique-se que copiou o Client ID completo (com `.apps.googleusercontent.com`)

### Problema: "Invalid Client Secret"
**Solução:** Não deixe espaços em branco ao copiar

### Problema: "API not enabled"
**Solução:** Volte ao PASSO 3 e clique em [ENABLE] para Google+ API

---

## 🔒 SEGURANÇA

⚠️ **NUNCA compartilhe:**
- Client ID
- Client Secret
- Arquivo JSON de credenciais

✅ **SEMPRE guarde:**
- Em arquivo seguro
- Não no código-fonte
- Não no GitHub
- Não compartilhe com ninguém

---

## 📱 PARA PRODUÇÃO (Depois)

Quando colocar em produção:

1. Adicione seu domínio:
   - JavaScript Origins: `https://seu-poker-ranking.com`
   - Redirect URI: `https://seu-poker-ranking.com/accounts/google/login/callback/`

2. Use HTTPS (não HTTP)

3. Configure DNS apontando para seu servidor

4. Use variáveis de ambiente para credenciais

---

## ✨ VOCÊ CONCLUIU!

Parabéns! 🎉

Agora você tem as credenciais do Google. Basta adicionar no Django Admin e seu Google OAuth vai funcionar!

**Próximo passo:** [Adicionar Credenciais no Django](#próximo-passo-adicionar-no-django)
