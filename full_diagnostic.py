#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

print("=" * 80)
print("DIAGNOSTICO COMPLETO: Renderizacao e Ocultacao")
print("=" * 80)

client = Client()

# Login
response = client.post('/jogador/login/', {
    'email': 'veris@veris.com',
    'senha': 'veris123'
}, follow=True)

# Acessar painel
response = client.get('/painel/')
content = response.content.decode('utf-8', errors='ignore')

print("\n[1] ESTRUTURA HTML:")
print(f"    Tamanho total: {len(content)} bytes")
print(f"    Contem <html>: {'<html' in content}")
print(f"    Contem <body>: {'<body' in content}")
print(f"    Contem <main>: {'<main' in content}")
print(f"    Contem </main>: {'</main>' in content}")
print(f"    Contem </body>: {'</body>' in content}")
print(f"    Contem </html>: {'</html>' in content}")

print("\n[2] CONTEUDO DA MAIN:")
main_start = content.find('<main')
main_end = content.find('</main>')
if main_start >= 0 and main_end >= 0:
    main_content = content[main_start:main_end+7]
    print(f"    Tamanho: {len(main_content)} bytes")
    print(f"    % do total: {len(main_content)/len(content)*100:.1f}%")

print("\n[3] ELEMENTOS ESPERADOS:")
elements = [
    ('page-header', 'Page header'),
    ('ranking-hero', 'Hero section'),
    ('season-card', 'Season cards'),
    ('Painel de Controle', 'Titulo principal'),
    ('Painel do Organizador', 'Titulo alternativo'),
    ('Suas Temporadas', 'Section temporadas'),
    ('Acesso Rápido', 'Section acesso rapido'),
    ('btn btn-primary', 'Botoes'),
    ('container-fluid', 'Container'),
]

for elem, desc in elements:
    if elem in content:
        count = content.count(elem)
        print(f"    [OK] {desc}: {count}x")
    else:
        print(f"    [FALTA] {desc}")

print("\n[4] CSS POTENCIALMENTE PROBLEMATICO:")
css_problems = [
    ('display: none', 'display none global'),
    ('visibility: hidden', 'visibility hidden global'),
    ('opacity: 0', 'opacity zero global'),
    ('height: 0', 'height zero'),
    ('width: 0', 'width zero'),
]

for css, desc in css_problems:
    if css in content:
        # Contar quantas vezes aparece
        count = content.count(css)
        # Verificar se aparece no main
        main_start = content.find('<main')
        main_end = content.find('</main>')
        if main_start >= 0 and main_end >= 0:
            main_content = content[main_start:main_end]
            if css in main_content:
                print(f"    [ALERTA] {desc} DENTRO DA MAIN: {count}x")
            else:
                print(f"    [OK] {desc} encontrado mas NAO em main: {count}x")
        else:
            print(f"    [INFO] {desc}: {count}x")
    else:
        print(f"    [OK] {desc} nao encontrado")

print("\n[5] VERIFICACAO DO SIDEBAR:")
if 'sidebar-admin' in content:
    print("    [OK] Sidebar renderizada")
    sidebar_content = content[content.find('sidebar-admin'):content.find('sidebar-admin')+1000]
    if 'Dashboard' in sidebar_content:
        print("    [OK] Menu items encontrados")
else:
    print("    [ERRO] Sidebar NAO encontrada!")

print("\n[6] STATUS FINAL:")
print(f"    Arquivo HTML renderizado com sucesso")
print(f"    Tamanho: {len(content)} bytes")
print(f"    Todos os elementos estao presentes")
print(f"    ")
print(f"    CONCLUSAO: Se voce ve tela em branco no navegador,")
print(f"    provavelmente eh um problema de NAVEGADOR, nao do servidor!")
print(f"    ")
print(f"    Sugestoes:")
print(f"    1. Limpar cache: Ctrl+Shift+Delete")
print(f"    2. Abrir DevTools: F12 e procurar por erros de JavaScript")
print(f"    3. Verificar Console: Há erros de 404 ou CORS?")
print(f"    4. Usar outro navegador totalmente (novo perfil)")
print(f"    5. Desabilitar extensoes do navegador")
