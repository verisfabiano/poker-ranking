"""
Teste para verificar se Railway está recebendo e retornando a página corretamente
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# URL da Railway
RAILWAY_URL = os.getenv("RAILWAY_URL", "https://web-production-09041up.railway.app")

# Tentar acessar /painel/ sem autenticação (deve redirecionar)
print("[1] Teste GET /painel/ SEM login")
response = requests.get(f"{RAILWAY_URL}/painel/", allow_redirects=False)
print(f"    Status: {response.status_code}")
print(f"    Headers: {dict(response.headers)}")
if response.status_code in [301, 302, 303, 307, 308]:
    print(f"    Redirect to: {response.headers.get('Location')}")

# Tentar acessar /signup/ sem autenticação
print("\n[2] Teste GET /signup/ SEM login")
response = requests.get(f"{RAILWAY_URL}/signup/")
print(f"    Status: {response.status_code}")
print(f"    Content-Length: {len(response.content)} bytes")
if len(response.content) > 100:
    print(f"    Primeiros 200 chars: {response.text[:200]}")
else:
    print(f"    [⚠️] Resposta muito pequena!")
    print(f"    Content: {response.text}")

# Verificar headers de segurança
print("\n[3] Headers da resposta")
for key, value in response.headers.items():
    if key.lower() in ['content-type', 'content-length', 'x-frame-options', 'x-content-type-options']:
        print(f"    {key}: {value}")
