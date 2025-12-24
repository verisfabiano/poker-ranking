import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

user = User.objects.get(username='veris')
client = Client()
client.force_login(user)
response = client.get('/painel/')

content = response.content.decode('utf-8')

# Verificar se o modal está com display: none
if 'selecionarTemporadaModal' in content:
    modal_match = re.search(r'<div[^>]*id="selecionarTemporadaModal"[^>]*>', content)
    if modal_match:
        modal_tag = modal_match.group(0)
        print('Modal tag:', modal_tag)
        if 'style="display: none"' in modal_tag:
            print('[OK] Modal tem display: none')
        else:
            print('[!] Modal NAO tem display: none')
else:
    print('[!] Modal nao encontrado')

# Verificar tamanho total
print(f'\nTamanho total: {len(content)} bytes')

# Verificar se página renderiza conteúdo
if '<main' in content:
    print('[OK] Main content area encontrada')
if 'Painel do Organizador' in content or 'Ranking das Temporadas' in content:
    print('[OK] Dashboard conteudo encontrado')
if 'Por Periodo' in content or 'Por Período' in content:
    print('[OK] Botao financeiro encontrado')
