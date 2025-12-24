import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import Client

# Teste 1: Acessar sem cookie/sessão
print('[TESTE 1] Sem autenticação')
client1 = Client()
r1 = client1.get('/signup/')
print(f'Status: {r1.status_code}')
print(f'Tamanho: {len(r1.content)} bytes')

content = r1.content.decode('utf-8')
# Verificar elementos principais
checks = [
    ('DOCTYPE', '<!DOCTYPE' in content),
    ('<html', '<html' in content),
    ('<body', '<body' in content),
    ('signup-container', 'signup-container' in content),
    ('form id="signupForm"', 'signupForm' in content),
    ('Criar Novo Clube', 'Criar Novo Clube' in content),
    ('<script', '<script' in content),
]

print('\nElementos encontrados:')
for name, found in checks:
    print(f'  {name:30} -> {found}')

# Teste 2: Com usuário autenticado (deve redirecionar)
print('\n[TESTE 2] Com autenticação (deve redirecionar)')
from django.contrib.auth.models import User
user = User.objects.filter(username='veris').first()
if user:
    client2 = Client()
    client2.force_login(user)
    r2 = client2.get('/signup/', follow=False)
    print(f'Status: {r2.status_code}')
    print(f'Redirect to: {r2.url if r2.status_code in [301, 302, 303, 307, 308] else "N/A"}')
else:
    print('Usuário veris não encontrado')
