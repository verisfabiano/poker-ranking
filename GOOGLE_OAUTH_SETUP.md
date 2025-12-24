# Google OAuth Setup - Instruções

## Passo 1: Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com
2. Clique em "Novo Projeto"
3. Nome do Projeto: "Poker Ranking"
4. Clique em "Criar"

## Passo 2: Ativar Google+ API

1. No menu superior, busque "Google+ API"
2. Clique em "Ativar"
3. Aguarde a ativação

## Passo 3: Criar OAuth Consent Screen

1. Na barra lateral, vá para: APIs e Serviços > OAuth Consent Screen
2. Escolha "Externo" (External)
3. Clique em "Criar"
4. Preencha os dados obrigatórios:
   - App name: "Poker Ranking"
   - Email de suporte: seu@email.com
   - Informações do desenvolvedor: seu@email.com

## Passo 4: Criar Credenciais OAuth 2.0

1. Vá para: APIs e Serviços > Credenciais
2. Clique em "Criar Credenciais" > "ID do cliente OAuth"
3. Selecione "Aplicativo da Web"
4. Preencha os dados:
   - Name: "Poker Ranking Web Client"
   - URIs autorizados de origem:
     * http://localhost:8000
     * http://localhost:8080
     * http://127.0.0.1:8000
     * http://127.0.0.1:8080
     * [Seu domínio de produção, ex: https://seu-poker-ranking.com]
   
   - URIs de redirecionamento autorizados:
     * http://localhost:8000/accounts/google/login/callback/
     * http://localhost:8080/accounts/google/login/callback/
     * http://127.0.0.1:8000/accounts/google/login/callback/
     * http://127.0.0.1:8080/accounts/google/login/callback/
     * [Sua URI de produção, ex: https://seu-poker-ranking.com/accounts/google/login/callback/]

5. Clique em "Criar"
6. Você receberá o Client ID e Client Secret
7. **GUARDE ESTES VALORES COM SEGURANÇA**

## Passo 5: Adicionar Credenciais no Django Admin

1. Inicie o servidor: `python manage.py runserver`
2. Acesse: http://localhost:8000/admin
3. Vá para: Sites (se não existir, crie com domain=localhost:8000)
4. Vá para: Social Applications
5. Clique em "Adicionar Social Application"
6. Preencha os dados:
   - Provider: Google
   - Name: Google OAuth
   - Client ID: [Cole seu Client ID do Google]
   - Secret key: [Cole seu Client Secret do Google]
   - Sites: Selecione o site padrão
7. Clique em "Salvar"

## Passo 6: Testar Login com Google

1. Acesse: http://localhost:8000/accounts/login/
2. Clique em "Entrar com Google"
3. Você será redirecionado para Google
4. Após autorizar, uma conta será criada automaticamente
5. Você será redirecionado para home

## Variáveis de Ambiente (Opcional para Segurança)

Para não deixar credenciais no código, você pode usar variáveis de ambiente:

```python
# No settings.py
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}

# As credenciais serão configuradas via Django Admin
```

E criar um arquivo `.env`:
```
GOOGLE_OAUTH_CLIENT_ID=seu_client_id_aqui
GOOGLE_OAUTH_CLIENT_SECRET=seu_client_secret_aqui
```

Depois usar:
```python
from django.conf import settings
client_id = settings.GOOGLE_OAUTH_CLIENT_ID
client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
```

## Troubleshooting

### Erro: "Redirect URI mismatch"
- Verifique se a URI no Google Console corresponde exatamente com a URL de login
- As URIs devem ser exatas (com trailing slash se necessário)

### Erro: "Invalid Client"
- Verifique se Client ID e Client Secret estão corretos
- Regenere as credenciais se necessário

### Social Application não aparece no Django
- Certifique-se que `allauth.socialaccount.providers.google` está em INSTALLED_APPS
- Execute `python manage.py migrate`

## Próximos Passos

1. Customizar perfil do jogador após login (coletar apelido, status, etc)
2. Conectar usuário OAuth com modelo Player existente
3. Adicionar verificação de email
4. Adicionar autenticação multi-tenant (cada site/clube com seu próprio OAuth)
