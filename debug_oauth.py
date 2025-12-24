#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print("=" * 60)
print("VERIFICAÇÃO DE CONFIGURAÇÃO OAUTH")
print("=" * 60)

# Verificar sites
print("\n1. SITES CONFIGURADOS:")
sites = Site.objects.all().values('id', 'domain', 'name')
for site in sites:
    print(f"   - ID: {site['id']}, Domain: {site['domain']}, Name: {site['name']}")

# Verificar Social Applications
print("\n2. SOCIAL APPLICATIONS:")
apps = SocialApp.objects.all()
for app in apps:
    print(f"\n   Provider: {app.provider}")
    print(f"   Name: {app.name}")
    print(f"   Client ID: {app.client_id}")
    print(f"   Client Secret: {app.secret[:20]}...")
    print(f"   Sites associados:")
    for site in app.sites.all():
        print(f"      - {site.domain}")

# Verificar settings
print("\n3. SETTINGS OAUTH:")
from django.conf import settings
print(f"   SITE_ID: {settings.SITE_ID}")
print(f"   LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
print(f"   SOCIALACCOUNT_AUTO_SIGNUP: {settings.SOCIALACCOUNT_AUTO_SIGNUP}")

print("\n" + "=" * 60)
