#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

print("=" * 60)
print("VERIFICANDO SOCIAL APPLICATIONS GOOGLE")
print("=" * 60)

apps = SocialApp.objects.filter(provider='google')
print(f"\nTotal Google apps: {apps.count()}")

for app in apps:
    print(f"\nID {app.id}: {app.name}")
    print(f"  Client ID: {app.client_id[:20]}...")
    print(f"  Sites: {list(app.sites.values_list('domain', flat=True))}")

# Se houver mais de 1, deletar os extras
if apps.count() > 1:
    print("\n⚠️ ENCONTRADO DUPLICATAS! Deletando extras...")
    for app in apps[1:]:
        print(f"Deletando ID {app.id}: {app.name}")
        app.delete()
    print("✅ Duplicatas removidas!")

print("\n" + "=" * 60)
