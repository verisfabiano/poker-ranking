#!/usr/bin/env python3
"""
Script para adicionar media queries de responsividade mobile em TODOS os templates
que ainda não têm otimização.
"""

import os
import re
from pathlib import Path

TEMPLATES_DIR = Path('core/templates')

# Templates já otimizados (não processar)
ALREADY_OPTIMIZED = {
    'base.html',  # template base tem o hamburger menu
    'player_home.html',
    'player_tournaments.html', 
    'player_profile.html',
    'player_login.html',
    'player_progress.html',
    'player_register.html',
    'player_register_public.html',
    'player_login_club.html',
    'player_form.html',
    'financial_dashboard.html',
    'financial_by_period.html',
    'ranking_avancado.html',
    'tournament_dashboard.html',
}

# CSS mobile padrão para diferentes tipos de template
MOBILE_CSS_TEMPLATES = {
    'default': '''@media (max-width: 576px) {
        h1, h2 { font-size: 1.25rem; }
        h3, h4 { font-size: 1.1rem; }
        h5, h6 { font-size: 1rem; }
        .container { padding: 0 0.75rem; }
        .card { margin-bottom: 0.75rem; }
        .card-body { padding: 0.75rem !important; }
        .btn { padding: 0.4rem 0.75rem; font-size: 0.9rem; }
        .table { font-size: 0.8rem; }
        table th, table td { padding: 0.4rem 0.25rem; }
    }
    
    @media (max-width: 992px) {
        h1, h2 { font-size: 1.5rem; }
    }''',
    
    'form': '''@media (max-width: 576px) {
        .card { margin: 0.5rem 0; }
        .card-body { padding: 1rem !important; }
        .card-header { padding: 0.75rem !important; }
        .form-label { font-size: 0.9rem; }
        .form-control, .form-select { font-size: 1rem; }
        .row { --bs-gutter-x: 0.5rem; }
        .col-md-6, .col-md-4 { max-width: 100%; }
    }''',
    
    'list': '''@media (max-width: 576px) {
        h2 { font-size: 1.25rem; }
        .btn-group { flex-wrap: wrap; }
        .table { font-size: 0.75rem; }
        .table th, .table td { padding: 0.4rem; }
        .badge { font-size: 0.65rem; padding: 0.25rem 0.4rem; }
    }''',
    
    'dashboard': '''@media (max-width: 576px) {
        h2 { font-size: 1.25rem; }
        .card-header { padding: 1rem 0.75rem !important; }
        .card-body { padding: 0.75rem !important; }
        .col-md-6, .col-md-4, .col-md-3, .col-lg-4 { margin-bottom: 0.75rem; }
        .row { --bs-gutter-x: 0.5rem; --bs-gutter-y: 0.75rem; }
    }''',
}

def should_process_template(filename):
    """Verifica se o template precisa ser processado"""
    if filename in ALREADY_OPTIMIZED:
        return False
    if not filename.endswith('.html'):
        return False
    # Ignora templates de confirmação e backup
    if 'confirm' in filename or 'bkp' in filename or 'check' in filename or 'output' in filename:
        return False
    return True

def has_extra_css_block(content):
    """Verifica se já tem block extra_css"""
    return '{% block extra_css %}' in content

def get_template_type(filename, content):
    """Determina o tipo de template para escolher CSS apropriado"""
    if 'form' in filename or 'create' in filename or 'edit' in filename:
        return 'form'
    if 'list' in filename or filename.startswith('players') or filename.startswith('tournament'):
        return 'list'
    if 'dashboard' in filename or 'painel' in filename or 'home' in filename:
        return 'dashboard'
    return 'default'

def add_extra_css_block(content, template_type):
    """Adiciona block extra_css depois de {% block title %}"""
    
    # Seleciona o CSS baseado no tipo
    css = MOBILE_CSS_TEMPLATES.get(template_type, MOBILE_CSS_TEMPLATES['default'])
    
    # Procura o local certo para inserir (após {% block title %})
    pattern = r'({% block title %}[^}]*{% endblock %})'
    
    extra_css_block = f"""

{{% block extra_css %}}
<style>
    {css}
</style>
{{% endblock %}}"""
    
    # Se já tem block extra_css, pula
    if has_extra_css_block(content):
        print(f"  ⚠️  Já tem extra_css block, pulando")
        return content
    
    # Insere após block title
    if re.search(pattern, content):
        new_content = re.sub(pattern, r'\1' + extra_css_block, content, count=1)
        return new_content
    
    # Se não achar block title, insere antes de {% block content %}
    if '{% block content %}' in content:
        new_content = content.replace('{% block content %}', extra_css_block + '\n\n{% block content %}')
        return new_content
    
    return content

def main():
    """Processa todos os templates"""
    print("🔍 Analisando templates...\n")
    
    templates = sorted([f for f in TEMPLATES_DIR.glob('*.html')])
    to_process = [f for f in templates if should_process_template(f.name)]
    
    print(f"Total de templates: {len(templates)}")
    print(f"Já otimizados: {len(ALREADY_OPTIMIZED)}")
    print(f"Para processar: {len(to_process)}\n")
    
    updated_count = 0
    skipped_count = 0
    
    for template_path in to_process:
        print(f"📄 {template_path.name}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Se já tem extra_css, pula
        if has_extra_css_block(content):
            print(f"  ✅ Já tem media queries")
            skipped_count += 1
            continue
        
        # Detecta tipo e adiciona CSS
        template_type = get_template_type(template_path.name, content)
        new_content = add_extra_css_block(content, template_type)
        
        if new_content != content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Adicionado media queries ({template_type})")
            updated_count += 1
        else:
            print(f"  ⚠️  Não conseguiu processar (estrutura diferente)")
            skipped_count += 1
    
    print(f"\n✨ Resultado:")
    print(f"  ✅ Atualizados: {updated_count}")
    print(f"  ⏭️  Já otimizados: {len(ALREADY_OPTIMIZED)}")
    print(f"  ⚠️  Pulados: {skipped_count}")
    print(f"\nTotal responsivo: {len(ALREADY_OPTIMIZED) + updated_count}/{len(templates)}")

if __name__ == '__main__':
    main()
