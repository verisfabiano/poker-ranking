#!/usr/bin/env python
import os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.test import Client

client = Client()
response = client.get('/signup/')
content = response.content.decode('utf-8')

# Procurar por problemas comuns
print("=== ANÁLISE DE ESTRUTURA HTML ===")

# Contar tags
tags = {
    '<div': len(re.findall(r'<div[^>]*>', content)),
    '</div': len(re.findall(r'</div>', content)),
    '<form': len(re.findall(r'<form[^>]*>', content)),
    '</form': len(re.findall(r'</form>', content)),
    '<input': len(re.findall(r'<input[^>]*>', content)),
    '<select': len(re.findall(r'<select[^>]*>', content)),
    '</select': len(re.findall(r'</select>', content)),
}

for tag, count in tags.items():
    print(f'{tag:15} -> {count}')

# Procurar por erros de sintaxe comuns
print("\n=== PROCURANDO POR ERROS ===")

# Tags não fechadas
if tags['<div'] != tags['</div']:
    print(f"⚠️  DIV: {tags['<div']} abertos vs {tags['</div']} fechados")

if tags['<form'] != tags['</form']:
    print(f"⚠️  FORM: {tags['<form']} abertos vs {tags['</form']} fechados")

if tags['<select'] != tags['</select']:
    print(f"⚠️  SELECT: {tags['<select']} abertos vs {tags['</select']} fechados")

# Procurar por template tags não fechadas
if content.count('{% if') != content.count('{% endif %}'):
    print(f"⚠️  Template IF: {content.count('{% if')} abertos vs {content.count('{% endif %}')} fechados")

# Procurar por script tags malformadas
script_match = re.search(r'<script[^>]*>.*?</script>', content, re.DOTALL)
if not script_match:
    print("⚠️  Nenhuma <script> tag encontrada (deve ter)")

# Teste de JavaScript
print("\n=== TESTE DE VALIDAÇÃO JS ===")
script_content = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if script_content:
    js = script_content.group(1)
    # Procurar por erros comuns de sintaxe
    if '.addEventListener' in js:
        print("[✓] addEventListener encontrado")
    if 'console.error' in js:
        print("[✓] console.error encontrado (tratamento de erros)")
    # Procurar por template tags em JS que não foram renderizadas
    if '{%' in js or '{{' in js:
        print("⚠️  Template tags não renderizadas em <script>!")

print("\n[OK] Se nenhuma aviso acima, HTML está bem formado")
