#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

client = Client()
client.login(username='testevris', password='testevris123')

response = client.get('/ranking/12/')
content = response.content.decode('utf-8')

# Procurar por palavras-chave para identificar o template
checks = [
    ('Evolução', 'evolution'),
    ('ranking_jogador', 'ranking_jogador.html'),
    ('minha_posicao', 'ranking_jogador.html (minha posição)'),
    ('Detalhamento', 'ranking.html (detalhamento)'),
    ('evolution-button', 'ranking.html (botão evolução)'),
]

print('Análise da página:')
for keyword, template in checks:
    found = keyword in content
    status = '✓' if found else '✗'
    print(f'  {keyword:20s} {status} {template}')

# Mostrar primeiros 1000 chars do conteúdo
print('\nPrimeiros 800 chars:')
body_start = content.find('<h2')
if body_start > 0:
    print(content[body_start:body_start+800])
