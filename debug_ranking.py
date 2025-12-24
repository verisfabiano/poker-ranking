#!/usr/bin/env python
"""
Script para debugar por que o ranking está zerado.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Season, TournamentResult, Tournament, TournamentType

print("=" * 70)
print("DEBUG - Investigando Ranking Zerado")
print("=" * 70)

# Temporada Teste
season = Season.objects.get(nome="Temporada Teste")
print(f"\n📊 Temporada: {season.nome}")
print(f"   Tipo de Cálculo: {season.tipo_calculo}")
print(f"   Tabela de Pontos: {season.get_tabela_pontos_fixos()}")

# Verificar torneios
tournaments = Tournament.objects.filter(season=season)
print(f"\n📅 Total de Torneios: {tournaments.count()}")
for t in tournaments:
    print(f"   - {t.nome} (Tipo: {t.tipo.nome if t.tipo else 'Sem tipo'})")
    if t.tipo:
        print(f"     Multiplicador: {t.tipo.multiplicador_pontos}")

# Verificar resultados
results = TournamentResult.objects.filter(tournament__season=season)
print(f"\n🎯 Total de Resultados: {results.count()}")

if results.count() > 0:
    print("\n   Amostra de resultados:")
    for r in results[:10]:
        print(f"   - {r.player.nome}: Posição {r.posicao} | Prêmio: R$ {r.premiacao_recebida}")

# Testar função de cálculo
print(f"\n⚙️ Testando cálculo de pontos:")
from core.views.ranking import _calcular_pontos_resultado

for tournament in tournaments[:1]:
    print(f"\n   Torneio: {tournament.nome}")
    for posicao in [1, 2, 3, 4, 5]:
        pontos = _calcular_pontos_resultado(tournament, posicao)
        print(f"   Posição {posicao}: {pontos} pontos")

# Testar build ranking
print(f"\n📊 Testando build ranking:")
from core.views.season import _build_ranking_for_season

ranking = _build_ranking_for_season(season)
print(f"   Ranking retornou: {len(ranking)} jogadores")

if ranking:
    print("\n   Top 5 do Ranking:")
    for item in ranking[:5]:
        print(f"   {item['posicao']}º - {item['nome']}: {item['pontos']} pts " +
              f"(Resultado: {item['pontos_resultado']}, Iniciais: {item['pontos_iniciais']})")

print("\n" + "=" * 70)
