#!/usr/bin/env python
"""
Teste de verificação de URLs e views
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser

print("=" * 70)
print("VERIFICAÇÃO DE URLS E VIEWS")
print("=" * 70)

# Lista de URLs críticas para verificar
urls_to_check = [
    ('login', 'player_login'),
    ('jogador_home', 'player_home'),
    ('torneios', 'tournaments_list_all'),
    ('seasons', 'seasons_list'),
    ('painel_home', 'painel_home'),
    ('ranking_avancado', None),  # precisa de season_id
]

print("\n✓ URLS REVERSÍVEIS")
errors = []
for url_name, view_name in urls_to_check:
    try:
        if url_name == 'ranking_avancado':
            # Esta URL precisa de parâmetro
            reverse(url_name, args=[1])
            print(f"  ✓ {url_name} (com parâmetro)")
        else:
            reverse(url_name)
            print(f"  ✓ {url_name}")
    except NoReverseMatch as e:
        errors.append(f"✗ {url_name}: {str(e)}")
        print(f"  ✗ {url_name}")

if errors:
    print("\n⚠ Erros encontrados:")
    for error in errors:
        print(f"  {error}")
else:
    print("\n  ✅ Todas as URLs estão configuradas!")

# Verificar imports das views
print("\n✓ IMPORTS DE VIEWS")
try:
    from core.views.player import player_home, player_register, select_tenant_register
    print("  ✓ Player views")
except ImportError as e:
    print(f"  ✗ Player views: {e}")

try:
    from core.views.tournament import tournaments_list_all
    print("  ✓ Tournament views")
except ImportError as e:
    print(f"  ✗ Tournament views: {e}")

try:
    from core.views.ranking import painel_home
    print("  ✓ Ranking views")
except ImportError as e:
    print(f"  ✗ Ranking views: {e}")

try:
    from core.views.season import seasons_list
    print("  ✓ Season views")
except ImportError as e:
    print(f"  ✗ Season views: {e}")

try:
    from core.views.auth import player_login, player_logout
    print("  ✓ Auth views")
except ImportError as e:
    print(f"  ✗ Auth views: {e}")

print("\n" + "=" * 70)
print("✅ VERIFICAÇÃO CONCLUÍDA!")
print("=" * 70)
