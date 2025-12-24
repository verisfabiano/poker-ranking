#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.sites.models import Site

print("=" * 60)
print("REMOVENDO SITE DUPLICADO")
print("=" * 60)

# Mostrar sites antes
print("\nSites ANTES:")
for site in Site.objects.all():
    print(f"  ID {site.id}: {site.domain}")

# Deletar example.com
example_site = Site.objects.filter(domain='example.com').first()
if example_site:
    print(f"\nDeletando: {example_site.domain} (ID {example_site.id})")
    example_site.delete()
    print("✅ Deletado!")

# Mostrar sites depois
print("\nSites DEPOIS:")
for site in Site.objects.all():
    print(f"  ID {site.id}: {site.domain}")

print("\n" + "=" * 60)
