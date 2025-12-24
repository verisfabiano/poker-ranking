#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament, Tenant
from django.utils import timezone

tenant = Tenant.objects.get(slug='espacopoker')
now = timezone.now()
days_back = 30
date_from = now - timedelta(days=days_back)

print(f"Data/Hora Atual: {now}")
print(f"Filtro de Período: últimos {days_back} dias")
print(f"Data Mínima para Incluir: {date_from}")
print()

tournaments = Tournament.objects.filter(tenant=tenant).order_by('-data')
print(f"Total de Torneios (espacopoker): {tournaments.count()}")
print("\n=== TODOS OS TORNEIOS ===")
for t in tournaments:
    diff = (now - t.data).days if t.data else None
    included = "✅" if t.data and t.data >= date_from else "❌"
    print(f"{included} {t.nome:30} | Data: {t.data} | ({diff} dias atrás)")

print("\n=== TORNEIOS INCLUSOS (últimos 30 dias) ===")
filtered = Tournament.objects.filter(tenant=tenant, data__gte=date_from).order_by('-data')
print(f"Total: {filtered.count()}")
for t in filtered:
    print(f"  ✅ {t.nome} | Data: {t.data}")
