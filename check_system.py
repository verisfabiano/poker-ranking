#!/usr/bin/env python
"""
Script de checagem geral do sistema Poker Ranking
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Tenant, TenantUser, Player, Season, Tournament
from django.db.models import Count

print("=" * 70)
print("CHECAGEM GERAL DO SISTEMA - POKER RANKING")
print("=" * 70)

# 1. Users
print("\n✓ USUÁRIOS")
admin_count = User.objects.filter(is_superuser=True).count()
staff_count = User.objects.filter(is_staff=True).count()
total_users = User.objects.count()
print(f"  Total: {total_users} usuários")
print(f"  Superusers: {admin_count}")
print(f"  Staff: {staff_count}")

# 2. Tenants
print("\n✓ TENANTS (CLUBES)")
tenants = Tenant.objects.all()
print(f"  Total: {tenants.count()} tenants")
for t in tenants:
    tu_count = TenantUser.objects.filter(tenant=t).count()
    ativo_status = "ATIVO" if t.ativo else "INATIVO"
    print(f"    - {t.nome} ({ativo_status}): {tu_count} usuários")

# 3. Players
print("\n✓ JOGADORES")
players = Player.objects.all()
print(f"  Total: {players.count()} jogadores")
players_with_user = Player.objects.exclude(user__isnull=True).count()
print(f"  Com usuário Django: {players_with_user}")

# 4. Seasons
print("\n✓ TEMPORADAS")
seasons = Season.objects.all()
print(f"  Total: {seasons.count()} temporadas")
active_seasons = Season.objects.filter(ativo=True).count()
print(f"  Ativas: {active_seasons}")

# 5. Tournaments
print("\n✓ TORNEIOS")
tournaments = Tournament.objects.all()
print(f"  Total: {tournaments.count()} torneios")
tournament_status = tournaments.values('status').annotate(count=Count('id'))
for status_dict in tournament_status:
    print(f"    - {status_dict['status']}: {status_dict['count']}")

# 6. TenantUser
print("\n✓ ACESSOS (TENANTUSER)")
tenant_users = TenantUser.objects.all()
print(f"  Total: {tenant_users.count()} acessos")
roles = tenant_users.values('role').annotate(count=Count('id'))
for role_dict in roles:
    print(f"    - Role '{role_dict['role']}': {role_dict['count']}")

# 7. Verificar integridade de relacionamentos
print("\n✓ INTEGRIDADE DE RELACIONAMENTOS")
errors = []

# Players sem User
players_no_user = Player.objects.filter(user__isnull=True).count()
if players_no_user > 0:
    errors.append(f"⚠ {players_no_user} jogadores sem User Django")

# TenantUsers órfãos (tenant inativo)
orphan_tenant_users = TenantUser.objects.filter(tenant__ativo=False).count()
if orphan_tenant_users > 0:
    errors.append(f"⚠ {orphan_tenant_users} acessos a tenants inativos")

# Tournaments sem Season
tournaments_no_season = Tournament.objects.filter(season__isnull=True).count()
if tournaments_no_season > 0:
    errors.append(f"⚠ {tournaments_no_season} torneios sem season")

if errors:
    print("  Problemas encontrados:")
    for error in errors:
        print(f"    {error}")
else:
    print("  ✅ Nenhum problema encontrado!")

print("\n" + "=" * 70)
print("✅ CHECAGEM CONCLUÍDA COM SUCESSO!")
print("=" * 70)
