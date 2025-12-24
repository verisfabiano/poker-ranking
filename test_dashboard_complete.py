#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tournament
from core.views.financial import financial_dashboard, calcular_financeiro_torneio
from django.test import RequestFactory
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Criar um request mock
factory = RequestFactory()
request = factory.get('/financeiro/')

# Adicionar tenant ao request (simulando middleware)
from core.models import Tenant
tenant = Tenant.objects.first()
request.tenant = tenant

# Adicionar user mock
request.user = User.objects.first() or User.objects.create(username='test', is_staff=True)

# Modificar get_GET para GET para passar dias
request.GET = {'days': '30'}

# Calcular financeiro dos últimos 30 dias
days = int(request.GET.get('days', 30))
date_from = timezone.now() - timedelta(days=days)

tournaments = Tournament.objects.filter(tenant=request.tenant, data__gte=date_from).order_by('-data')

print(f"\n{'='*70}")
print(f"DASHBOARD FINANCEIRO - Últimos {days} dias")
print(f"{'='*70}\n")

print(f"Torneios encontrados: {tournaments.count()}\n")

total_faturamento = 0
total_rake = 0
total_pote = 0
total_premios = 0

for tournament in tournaments:
    result = calcular_financeiro_torneio(tournament)
    
    print(f"📊 {tournament.nome}")
    print(f"   Data: {tournament.data.strftime('%d/%m/%Y') if tournament.data else 'N/A'}")
    print(f"   Faturamento: R$ {result['faturamento_bruto']:>10.2f}")
    print(f"   Rake:        R$ {result['rake_total']:>10.2f}")
    print(f"   Prêmios:     R$ {result['premios_pagos']:>10.2f}")
    print(f"   Saldo:       R$ {result['saldo']:>10.2f}")
    print()
    
    total_faturamento += result['faturamento_bruto']
    total_rake += result['rake_total']
    total_pote += result['pote_total']
    total_premios += result['premios_pagos']

print(f"{'='*70}")
print(f"TOTAIS")
print(f"{'='*70}")
print(f"Faturamento Total:  R$ {total_faturamento:.2f}")
print(f"Rake Total:         R$ {total_rake:.2f}")
print(f"Pote Total:         R$ {total_pote:.2f}")
print(f"Prêmios Total:      R$ {total_premios:.2f}")
print(f"Lucro Total:        R$ {(total_faturamento - total_premios):.2f}")
print(f"{'='*70}\n")
