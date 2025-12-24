import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

import re
from django.test import Client
from django.contrib.auth.models import User

user = User.objects.get(username='veris')
client = Client()
client.force_login(user)
response = client.get('/painel/')
content = response.content.decode('utf-8')

# Procurar por problemas específicos que podem causar branco
print("=== DIAGNÓSTICO PÁGINA EM BRANCO ===\n")

# 1. Verifica se há container visibility hidden
if 'visibility: hidden' in content:
    print("[⚠️] Found visibility: hidden")

# 2. Verifica se há container com display none
if 'display: none' in content:
    idx = content.find('display: none')
    print(f"[⚠️] Found 'display: none' at position {idx}")
    print(f"    Context: {content[max(0,idx-50):idx+50]}")

# 3. Verifica se container principal está visible
if '.main-content' in content or 'main-content' in content:
    print("[✓] Found main-content class")

# 4. Verifica Bootstrap CDN
if 'cdn.jsdelivr.net' in content or 'bootstrap' in content:
    print("[✓] Bootstrap CDN presente")

# 5. Procura por erros de JavaScript que podem estar impedindo render
if 'throw new Error' in content:
    print("[⚠️] JavaScript error throw encontrado")

if 'uncaught' in content.lower():
    print("[⚠️] 'uncaught' error encontrado")

# 6. Verifica dimensões que podem estar escondendo
if 'height: 0' in content or 'width: 0' in content:
    print("[⚠️] Found height: 0 or width: 0 styles")

# 7. Procura por CSS Grid/Flex que pode estar quebrado
styles_count = len(re.findall(r'<style[^>]*>', content))
print(f"\n[✓] <style> tags: {styles_count}")

# 8. Verifica se há mais de um container vazio
empty_divs = len(re.findall(r'<div[^>]*>\s*</div>', content))
print(f"[?] Empty <div> tags: {empty_divs}")

# 9. Verifica main area
if '<main' in content:
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
    if main_match:
        main_content = main_match.group(1)
        print(f"[✓] <main> tag found, content size: {len(main_content)} bytes")
        if len(main_content) < 100:
            print(f"    [⚠️] Main content muito pequeno!")
            print(f"    Content: {main_content.strip()[:200]}")
else:
    print("[?] No <main> tag found")

# 10. Verifica se sidebar é largo demais
if 'sidebar-width:' in content or '--sidebar-width:' in content:
    match = re.search(r'--sidebar-width:\s*([^;]+)', content)
    if match:
        width = match.group(1)
        print(f"[?] Sidebar width: {width}")
        if '260px' in width or '300px' in width:
            print(f"    Check if main content has left margin")

print("\n=== RESUMO ===")
print(f"Total HTML: {len(content)} bytes")
print(f"Total CSS: {len(re.findall(r'<style[^>]*>.*?</style>', content, re.DOTALL)[0]) if re.findall(r'<style[^>]*>.*?</style>', content, re.DOTALL) else 0} bytes")
