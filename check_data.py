#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print("=" * 60)
print("VERIFICAÇÃO COMPLETA SOCIAL APPS")
print("=" * 60)

# Mostrar todas as Social Apps
all_apps = SocialApp.objects.all()
print(f"\nTOTAL DE SOCIAL APPS: {all_apps.count()}")

for app in all_apps:
    print(f"\nID: {app.id}")
    print(f"  Provider: {app.provider}")
    print(f"  Name: {app.name}")
    print(f"  Client ID: {app.client_id[:30]}...")
    print(f"  Sites: {list(app.sites.values_list('domain', flat=True))}")

# Verificar sites
print("\n" + "=" * 60)
print("SITES CONFIGURADOS")
print("=" * 60)

sites = Site.objects.all()
print(f"\nTOTAL DE SITES: {sites.count()}")
for site in sites:
    print(f"  ID {site.id}: {site.domain}")

print("\n" + "=" * 60)
