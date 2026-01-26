# 🚀 Guia Completo de Migração para Hostinger

**Data**: Janeiro 2026  
**Projeto**: PokerClube Ranking  
**Tempo Estimado**: 3-4 horas  
**Nível de Dificuldade**: Moderado

---

## 📋 Pré-Requisitos

### Conta Hostinger
- [ ] Plano com suporte a **Python 3.9+** e **pip**
- [ ] Acesso ao **painel de controle** (cPanel ou Hostinger painel)
- [ ] PostgreSQL gerenciado OU capacidade de criar banco próprio
- [ ] SSH ativado na conta
- [ ] Domínio(s) apontando para Hostinger

### Informações Necessárias
```
✓ URL de produção (ex: www.pokerranking.com)
✓ Subdomínios dos clubes (ex: club1.pokerranking.com)
✓ Credenciais atuais do banco de dados
✓ Chave secreta do Google OAuth (CLIENT_ID, CLIENT_SECRET)
✓ Email para SMTP da Hostinger
✓ Backup completo do banco de dados atual
```

---

## 🔧 FASE 1: Preparação do Código

### 1.1 Atualizar Settings para Produção

**Arquivo**: `backend/settings.py`

```python
# ===== ANTES (desenvolvimento) =====
DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "django-insecure-..."  # Padrão Django

# ===== DEPOIS (produção) =====
DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "www.pokerranking.com").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "mudar-em-producao")
```

**Mudanças específicas**:

```python
# 1. Segurança HTTPS
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", 
    "https://www.pokerranking.com"
).split(",")

SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}

# 2. Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/user/public_html/logs/django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# 3. Banco de Dados
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost/pokerranking"
        ),
        conn_max_age=600,
    )
}

# 4. Static Files (Hostinger)
STATIC_URL = "/static/"
STATIC_ROOT = "/home/user/public_html/staticfiles"  # Adaptar ao usuário
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 5. Media Files
MEDIA_URL = "/media/"
MEDIA_ROOT = "/home/user/public_html/media"  # Adaptar ao usuário
```

### 1.2 Verificar requirements.txt

**Seu arquivo atual está OK**, mas adicionar pacotes para produção:

```plaintext
# requirements.txt ATUAL (MANTER)
asgiref==3.11.0
dj-database-url==3.0.1
Django==5.2.9
gunicorn==23.0.0
markdown2==2.4.12
packaging==25.0
Pillow==11.0.0
psycopg2-binary==2.9.11
PyJWT==2.10.1
requests==2.32.5
sqlparse==0.5.4
tzdata==2025.2
whitenoise==6.11.0
cryptography==46.0.3

# ADICIONAR para Hostinger
python-decouple==3.8
python-dotenv==1.0.0
```

### 1.3 Criar .env para Hostinger

**Arquivo**: `.env` (raiz do projeto)

```bash
# Segurança
SECRET_KEY=gera_uma_chave_super_segura_aqui_com_32_caracteres
DEBUG=False
ALLOWED_HOSTS=www.pokerranking.com,pokerranking.com,club1.pokerranking.com,club2.pokerranking.com
SECURE_SSL_REDIRECT=True

# Banco de Dados (Hostinger fornecerá)
DATABASE_URL=postgresql://hostinger_user:senha_forte_123@localhost:5432/pokerranking_db

# Google OAuth
GOOGLE_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_OAUTH_REDIRECT_URI=https://www.pokerranking.com/auth/callback

# Email SMTP (Hostinger)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=seu_email@seudominio.com
EMAIL_HOST_PASSWORD=sua_senha_email

# Paths
STATIC_ROOT=/home/seu_usuario/public_html/staticfiles
MEDIA_ROOT=/home/seu_usuario/public_html/media
```

⚠️ **IMPORTANTE**: Adicionar `.env` ao `.gitignore` se não estiver:

```bash
# .gitignore
.env
.env.local
*.log
```

### 1.4 Gerar SECRET_KEY Segura

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar a saída e colocar em `SECRET_KEY=...` no `.env`

---

## 📦 FASE 2: Preparação do Banco de Dados

### 2.1 Fazer Backup Local

**Seu banco atual**:

```bash
# Se SQLite
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Se PostgreSQL
pg_dump -U seu_usuario seu_banco > backup_pokerranking_$(date +%Y%m%d).sql
```

### 2.2 Exportar Dados (melhor opção)

```bash
# Fazer dump do banco atual como fixture Django
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup_dados.json

# OU criar SQL puro
python manage.py dumpdata --format=sql > backup_dados.sql
```

### 2.3 Opções de Banco na Hostinger

#### Opção A: PostgreSQL Gerenciado (Recomendado)
- Hostinger fornece automaticamente
- Credenciais no painel → Databases
- Sem manutenção

#### Opção B: PostgreSQL Servidor Externo
```bash
# Se usar provedor externo (Heroku, Railway, etc)
DATABASE_URL=postgresql://user:pass@provider.com:5432/db
```

#### Opção C: SQLite (Não Recomendado)
- Funciona, mas não escalável
- Problemas com concorrência
- Evitar para produção multi-tenant

---

## 🏢 FASE 3: Configuração na Hostinger

### 3.1 Criar Banco de Dados (Painel Hostinger)

1. **Acessar**: Painel Hostinger → Bancos de Dados
2. **Criar novo**:
   - Nome: `pokerranking_db`
   - Usuário: `pokerranking_user`
   - Senha: (Gerar senha forte - copiar para `.env`)
3. **Anotar**: Host, Porta (padrão 5432), Banco, Usuário, Senha
4. **Atualizar `.env`**:
   ```
   DATABASE_URL=postgresql://pokerranking_user:senha@localhost:5432/pokerranking_db
   ```

### 3.2 Criar Pastas Essenciais (SSH)

```bash
# Conectar via SSH
ssh seu_usuario@seu_host.hostinger.com

# Criar estrutura
mkdir -p ~/public_html/staticfiles
mkdir -p ~/public_html/media
mkdir -p ~/public_html/logs
chmod 755 ~/public_html/staticfiles
chmod 755 ~/public_html/media
chmod 755 ~/public_html/logs
```

### 3.3 Configurar Python & Virtual Environment

```bash
# SSH conectado

# 1. Verificar Python
python3 --version  # Deve ser 3.9+

# 2. Criar venv
cd ~/public_html
python3 -m venv venv

# 3. Ativar
source venv/bin/activate

# 4. Atualizar pip
pip install --upgrade pip

# 5. Instalar dependências
pip install -r requirements.txt
```

### 3.4 Criar Arquivo de Inicialização (Hostinger)

**Arquivo**: `~/public_html/passenger_wsgi.py` (para Hostinger)

```python
import sys
import os

# Adicionar projeto ao path
sys.path.insert(0, '/home/seu_usuario/public_html')

# Ativar venv
os.environ['VIRTUAL_ENV'] = '/home/seu_usuario/public_html/venv'
sys.path.insert(0, '/home/seu_usuario/public_html/venv/lib/python3.10/site-packages')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Importar e retornar aplicação WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 3.5 Configurar .htaccess

**Arquivo**: `~/public_html/.htaccess`

```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    
    # Redirecionar HTTP para HTTPS
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
    
    # Redirecionar para Django via WSGI
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]
</IfModule>
```

---

## 🚀 FASE 4: Deploy (Enviar Código)

### 4.1 Opção A: Git Push (Recomendado)

```bash
# Localmente
git add .
git commit -m "Prepare for Hostinger migration"
git push origin main

# SSH Hostinger
cd ~/public_html
git clone https://github.com/seu_usuario/poker_ranking.git .

# OU se já existe repo
git pull origin main
```

### 4.2 Opção B: FTP/SFTP

Usar cliente (FileZilla) para enviar pasta do projeto para `~/public_html`

### 4.3 Copiar .env e Dados

```bash
# SSH Hostinger
cd ~/public_html

# Copiar .env (criar manualmente é mais seguro)
nano .env
# Colar conteúdo do .env local (NUNCA via git)

# Copiar backup do banco (se tiver)
sftp seu_usuario@seu_host.hostinger.com
put backup_dados.json
exit
```

---

## 🔄 FASE 5: Inicializar Banco de Dados

### 5.1 Executar Migrations

```bash
# SSH Hostinger
cd ~/public_html
source venv/bin/activate

# Criar tabelas
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 5.2 Carregar Dados (se backup)

```bash
# Se tem backup JSON
python manage.py loaddata backup_dados.json

# OU se vem de PostgreSQL
# (já foi feito na configuração do banco)
```

### 5.3 Criar Superuser

```bash
python manage.py createsuperuser
# Inserir: username, email, password
```

---

## 🔐 FASE 6: Configurar Google OAuth

### 6.1 Atualizar Google Cloud Console

1. **Acessar**: [Google Cloud Console](https://console.cloud.google.com)
2. **OAuth 2.0 Credentials**:
   - Editar credencial existente
   - **Authorized redirect URIs** adicionar:
     ```
     https://www.pokerranking.com/auth/callback
     https://pokerranking.com/auth/callback
     https://admin.pokerranking.com/auth/callback
     ```
   - Se tiver subdomínios por clube:
     ```
     https://club1.pokerranking.com/auth/callback
     https://club2.pokerranking.com/auth/callback
     ```
   - Salvar

### 6.2 Verificar Settings do Django

```python
# backend/settings.py
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}
```

---

## 📧 FASE 7: Configurar Email SMTP

### 7.1 Obter Credenciais Hostinger

1. **Painel Hostinger** → Email
2. **Criar** novo email (ex: noreply@seudominio.com)
3. **Anotar**:
   - Email: noreply@seudominio.com
   - Senha: (gerar)
   - SMTP: smtp.hostinger.com
   - Porta: 465 (SSL) ou 587 (TLS)

### 7.2 Testar Email

```bash
# SSH Hostinger
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test',
    'Teste de email',
    'noreply@seudominio.com',
    ['seu_email@example.com'],
    fail_silently=False
)
```

---

## ✅ FASE 8: Testes Pós-Migração

### 8.1 Testes Básicos

```bash
# SSH Hostinger - verificar status
cd ~/public_html

# Verificar se Django funciona
python manage.py check

# Verificar conectividade banco
python manage.py dbshell
SELECT 1;  # Deve retornar 1
\q

# Verificar arquivos estáticos foram coletados
ls -la staticfiles/
```

### 8.2 Testes no Browser

**Checklist**:
- [ ] Site abre em https://www.pokerranking.com
- [ ] Página inicial carrega (HTML, CSS, JS)
- [ ] Login funciona
- [ ] Google OAuth funciona
- [ ] Dashboard carrega dados
- [ ] Arquivo de log criado em ~/public_html/logs/
- [ ] Imagens/media carregam

### 8.3 Teste de Subdomínios

```bash
# Localmente: editar /etc/hosts (Windows: C:\Windows\System32\drivers\etc\hosts)
# 127.0.0.1    club1.pokerranking.local
# 127.0.0.1    club2.pokerranking.local

# Depois apontar no DNS real do Hostinger
# Criar registros A:
# club1.pokerranking.com → IP Hostinger
# club2.pokerranking.com → IP Hostinger
```

### 8.4 Verificar Logs de Erro

```bash
# SSH Hostinger
tail -f ~/public_html/logs/django_error.log

# Se não houver erros, está tudo bem
# CTRL+C para sair
```

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'django'"

```bash
# SSH Hostinger
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "connection refused" ao banco

```bash
# Verificar credenciais no .env
cat .env | grep DATABASE_URL

# Testar conexão
python manage.py dbshell

# Se falhar, checar:
# 1. Dados corretos em .env
# 2. Banco realmente criado no Hostinger
# 3. Firewall liberou acesso
```

### Erro: 500 ao acessar site

```bash
# Verificar logs
tail -f ~/public_html/logs/django_error.log

# Habilitar DEBUG temporariamente para ver erro
# .env: DEBUG=True (apenas para diagnóstico!)
```

### Estática não carrega (CSS/JS em branco)

```bash
# SSH Hostinger
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Verificar permissões
ls -la staticfiles/
chmod -R 755 staticfiles/
```

### Google OAuth não funciona

1. Verificar **REDIRECT_URI** no Google Cloud = URL da Hostinger
2. Verificar **CLIENT_ID** e **CLIENT_SECRET** corretos no `.env`
3. Limpar cookies/cache do browser

### Email não funciona

```bash
# SSH Hostinger - teste manual
python manage.py shell

from django.conf import settings
print(settings.EMAIL_HOST)
print(settings.EMAIL_PORT)

# Se valores vazios, .env não foi lido
# Reiniciar servidor:
touch passenger_wsgi.py  # Força reinicio
```

---

## 📋 Checklist Final

- [ ] Code pushed para Hostinger (via Git)
- [ ] `.env` criado com todas variáveis
- [ ] Banco PostgreSQL criado e funcionando
- [ ] `python manage.py migrate` executado
- [ ] `python manage.py collectstatic` executado
- [ ] Superuser criado
- [ ] Google OAuth URIs atualizadas
- [ ] Email SMTP testado
- [ ] DNS apontando para Hostinger
- [ ] HTTPS funcionando (certificado Let's Encrypt auto)
- [ ] Site abre sem erros
- [ ] Login funciona
- [ ] Dashboard carrega dados reais
- [ ] Subdomínios dos clubes funcionam

---

## 📞 Suporte Hostinger

- **Chat ao vivo**: Painel Hostinger → Suporte
- **Tickets**: Email support@hostinger.com
- **Documentação**: https://support.hostinger.com
- **Comunidade Django**: https://stackoverflow.com/questions/tagged/django+hostinger

---

## 🎯 Próximos Passos Recomendados

1. **Monitorar durante 1 semana** erros de produção
2. **Fazer backup diário** do banco em Hostinger
3. **Configurar alertas** de erro 500
4. **Documentar URLs finais** para equipe
5. **Testar fluxo completo** com dados reais

**Sucesso na migração! 🚀**
