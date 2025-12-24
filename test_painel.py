import os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

user = User.objects.filter(username='veris').first()
client = Client()
client.force_login(user)
response = client.get('/painel/')
content = response.content.decode('utf-8')

print('=== RECURSOS CARREGADOS ===')

# CDN links
cdns = re.findall(r'(https?://[^\s"\'<>]+\.(js|css))', content)
print(f'\nScripts/Styles (CDN):')
for cdn_tuple in set(cdns):
    print(f'  {cdn_tuple[0]}')

# Procurar por erros de console
if 'console.error' in content:
    print('\n[⚠️] console.error encontrado')
if 'console.log' in content:
    print('[✓] console.log presente')

# Procurar por template tags não renderizadas
template_tags = re.findall(r'(\{\{.*?\}\}|\{%.*?%\})', content)
if template_tags:
    print(f'\n[⚠️] Template tags não renderizadas: {len(template_tags)}')
    for match in template_tags[:5]:
        print(f'  {match}')
else:
    print('\n[✓] Nenhuma template tag não renderizada')

# Procurar por <style> tags inline que podem estar escondendo conteúdo
styles = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
print(f'\n=== ANÁLISE DE CSS ===')
print(f'Inline <style> tags: {len(styles)}')

for i, style in enumerate(styles[:2]):
    # Procurar por CSS que esconde elementos
    if 'display: none' in style:
        lines = style.split('\n')
        for j, line in enumerate(lines):
            if 'display: none' in line:
                print(f'Style block {i}, linha {j}: {line.strip()}')

print(f'\nTamanho total CSS: {sum(len(s) for s in styles)} bytes')

# Procurar por main content area vazia
main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
if main_match:
    main_content = main_match.group(1).strip()
    print(f'\n=== MAIN CONTENT ===')
    print(f'Tamanho: {len(main_content)} bytes')
    print(f'Primeiros 200 chars: {main_content[:200]}')
else:
    print('\n[⚠️] Nenhuma <main> tag encontrada')
