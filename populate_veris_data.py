#!/usr/bin/env python
"""
Script para popular dados de teste no Veris Poker.
Cria: Temporadas, Torneios, Jogadores, Resultados e Prêmios.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta, date
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from core.models import (
    Tenant, Player, Season, Tournament, TournamentType, 
    TournamentEntry, TournamentResult, TournamentPlayerPurchase,
    PlayerStatistics, BlindStructure, BlindLevel
)

def populate_veris_data():
    """Função principal para popular dados no Veris Poker"""
    
    # Obter ou criar o tenant Veris
    tenant, created = Tenant.objects.get_or_create(
        slug='veris-poker',
        defaults={
            'nome': 'Veris Poker',
            'descricao': 'Sistema de ranking Veris Poker',
            'ativo': True,
            'club_email': 'contato@verispoker.com.br',
            'club_phone': '11999999999',
        }
    )
    
    print("\n" + "="*60)
    print("  POPULAÇÃO DE DADOS - VERIS POKER")
    print("="*60 + "\n")
    
    print(f"✓ Tenant: {tenant.nome} (ID: {tenant.id})\n")
    
    # Criar estrutura de blinds
    print("1. Criando Estrutura de Blinds...")
    structure, created = BlindStructure.objects.get_or_create(
        nome='Padrão 20 minutos',
        tenant=tenant,
        defaults={
            'descricao': 'Estrutura padrão com blinds de 20 em 20 minutos',
        }
    )
    
    if created:
        blind_levels = [
            (1, 10, 20, 0, 20, False),
            (2, 20, 40, 0, 20, False),
            (3, 50, 100, 10, 20, False),
            (4, 100, 200, 20, 20, False),
            (5, 200, 400, 40, 20, False),
            (6, 0, 0, 0, 15, True),
            (7, 400, 800, 80, 20, False),
            (8, 800, 1600, 160, 20, False),
            (9, 1600, 3200, 320, 20, False),
            (10, 3200, 6400, 640, 20, False),
        ]
        
        for ordem, sb, bb, ante, tempo, is_break in blind_levels:
            BlindLevel.objects.create(
                structure=structure,
                tenant=tenant,
                ordem=ordem,
                small_blind=sb,
                big_blind=bb,
                ante=ante,
                tempo_minutos=tempo,
                is_break=is_break,
            )
        print(f"✓ Estrutura de blinds criada\n")
    else:
        print(f"✓ Estrutura de blinds existente\n")
    
    # Criar tipo de torneio
    print("2. Criando Tipo de Torneio...")
    tipo_torneio, created = TournamentType.objects.get_or_create(
        nome='Texas Hold\'em',
        tenant=tenant,
        defaults={
            'descricao': 'Torneio clássico de Texas Hold\'em',
            'buyin_padrao': Decimal('100.00'),
            'rake_padrao': Decimal('10.00'),
            'multiplicador_pontos': Decimal('1.00'),
        }
    )
    print(f"✓ Tipo de torneio criado\n")
    
    # Criar jogadores
    print("3. Criando Jogadores...")
    nomes_jogadores = [
        ('João Silva', 'Joãozinho'),
        ('Pedro Santos', 'Pedoca'),
        ('Carlos Oliveira', 'Charlie'),
        ('Lucas Costa', 'Luc'),
        ('Felipe Alves', 'Flip'),
        ('Marcos Gomes', 'Marquinhos'),
        ('Diego Ferreira', 'Diego'),
        ('Bruno Martins', 'Brunão'),
        ('Rafael Rocha', 'Rafa'),
        ('Thiago Pinto', 'Thiago'),
        ('Gustavo Souza', 'Guto'),
        ('André Ribeiro', 'André'),
        ('Tiago Mendes', 'Tiaguinho'),
        ('Victor Lima', 'Vitão'),
        ('Fabiano Verís', 'Fabiano'),
    ]
    
    jogadores = []
    for nome, apelido in nomes_jogadores:
        player, created = Player.objects.get_or_create(
            nome=nome,
            tenant=tenant,
            defaults={
                'apelido': apelido,
                'status': 'ATIVO',
                'ativo': True,
            }
        )
        jogadores.append(player)
    
    print(f"✓ {len(jogadores)} jogadores criados\n")
    
    # Criar temporadas
    print("4. Criando Temporadas...")
    temporadas = []
    
    for ano in [2024, 2025]:
        season, created = Season.objects.get_or_create(
            nome=f'Temporada {ano}',
            tenant=tenant,
            defaults={
                'data_inicio': date(ano, 1, 1),
                'data_fim': date(ano, 12, 31),
                'ativo': True,
                'tipo_calculo': 'DINAMICO',
            }
        )
        temporadas.append(season)
    
    print(f"✓ {len(temporadas)} temporadas criadas\n")
    
    # Criar torneios e resultados
    print("5. Criando Torneios e Resultados...\n")
    
    nomes_torneios = [
        'Semanal #1 - Quarta',
        'Semanal #2 - Sexta',
        'Especial Sábado',
        'Torneio da Casa',
        'Mega Torneio',
    ]
    
    data_base = timezone.now().replace(hour=20, minute=0, second=0, microsecond=0)
    total_torneios = 0
    total_resultados = 0
    
    for temporada in temporadas:
        print(f"  Temporada {temporada.nome}:")
        
        for i, nome in enumerate(nomes_torneios):
            data = data_base - timedelta(days=random.randint(1, 20))
            
            torneio, created = Tournament.objects.get_or_create(
                nome=nome,
                season=temporada,
                tenant=tenant,
                data=data,
                defaults={
                    'tipo': tipo_torneio,
                    'descricao': f'Torneio de teste #{i+1}',
                    'buyin': Decimal('100.00'),
                    'buyin_chips': 10000,
                    'rake_type': 'FIXO',
                    'rake_valor': Decimal('10.00'),
                    'permite_rebuy': True,
                    'rebuy_valor': Decimal('100.00'),
                    'rebuy_chips': 10000,
                    'permite_addon': True,
                    'addon_valor': Decimal('100.00'),
                    'addon_chips': 5000,
                    'status': 'ENCERRADO',
                    'blind_structure': structure,
                    'total_jogadores': 0,
                }
            )
            
            if created:
                num_inscritos = random.randint(8, 15)
                inscritos = random.sample(jogadores, min(num_inscritos, len(jogadores)))
                
                for jogador in inscritos:
                    entry, _ = TournamentEntry.objects.get_or_create(
                        tournament=torneio,
                        player=jogador,
                        tenant=tenant,
                        defaults={
                            'confirmou_presenca': True,
                            'confirmado_pelo_admin': True,
                        }
                    )
                    
                    if random.random() < 0.4:
                        TournamentPlayerPurchase.objects.get_or_create(
                            tournament=torneio,
                            player=jogador,
                            tipo='REBUY',
                            defaults={
                                'valor': torneio.rebuy_valor or Decimal('100.00'),
                                'quantidade': random.randint(1, 2),
                                'tenant': tenant,
                            }
                        )
                    
                    if random.random() < 0.3:
                        TournamentPlayerPurchase.objects.get_or_create(
                            tournament=torneio,
                            player=jogador,
                            tipo='ADDON',
                            defaults={
                                'valor': torneio.addon_valor or Decimal('100.00'),
                                'quantidade': 1,
                                'tenant': tenant,
                            }
                        )
                
                torneio.total_jogadores = len(inscritos)
                torneio.save()
                
                # Criar resultados
                posicoes = list(range(1, len(inscritos) + 1))
                random.shuffle(posicoes)
                
                for idx, jogador in enumerate(inscritos):
                    posicao = posicoes[idx]
                    
                    if posicao == 1:
                        premiacao = Decimal('500.00')
                    elif posicao == 2:
                        premiacao = Decimal('300.00')
                    elif posicao == 3:
                        premiacao = Decimal('150.00')
                    elif posicao <= 5:
                        premiacao = Decimal('100.00')
                    else:
                        premiacao = Decimal('0.00')
                    
                    resultado, _ = TournamentResult.objects.get_or_create(
                        tournament=torneio,
                        player=jogador,
                        tenant=tenant,
                        defaults={
                            'posicao': posicao,
                            'pontos_base': 0,
                            'premiacao_recebida': premiacao,
                        }
                    )
                    
                    resultado.calcular_pontos()
                    resultado.save()
                    total_resultados += 1
                
                total_torneios += 1
                print(f"    ✓ {nome} ({len(inscritos)} inscritos)")
        
        # Recalcular estatísticas
        recalcular_stats_temporada(temporada, tenant, jogadores)
        print()
    
    print("="*60)
    print("  ✓ POPULAÇÃO DE DADOS CONCLUÍDA!")
    print("="*60)
    print(f"\nResumo:")
    print(f"  • Tenant: {tenant.nome}")
    print(f"  • Jogadores: {len(jogadores)}")
    print(f"  • Temporadas: {len(temporadas)}")
    print(f"  • Torneios: {total_torneios}")
    print(f"  • Resultados: {total_resultados}")
    print(f"\nAgora acesse: http://localhost:8000/ranking/\n")

def recalcular_stats_temporada(temporada, tenant, jogadores):
    """Recalcula estatísticas para uma temporada"""
    from django.db.models import Sum
    
    for player in jogadores:
        resultados = TournamentResult.objects.filter(
            tournament__season=temporada,
            tournament__tenant=tenant,
            player=player,
        )
        
        if not resultados.exists():
            continue
        
        vitoria = resultados.filter(posicao=1).count()
        top_3 = resultados.filter(posicao__lte=3).count()
        top_5 = resultados.filter(posicao__lte=5).count()
        total_torneios = resultados.count()
        
        total_premio = resultados.aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or Decimal('0')
        
        total_buyin = Decimal('0')
        for resultado in resultados:
            torneio = resultado.tournament
            total_buyin += Decimal(torneio.buyin)
            
            rebuys = TournamentPlayerPurchase.objects.filter(
                tournament=torneio,
                player=player,
                tipo__in=['REBUY', 'REBUY_DUPLO']
            ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
            total_buyin += Decimal(rebuys)
            
            addons = TournamentPlayerPurchase.objects.filter(
                tournament=torneio,
                player=player,
                tipo='ADDON'
            ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
            total_buyin += Decimal(addons)
        
        if total_buyin > 0:
            roi = ((total_premio - total_buyin) / total_buyin) * 100
        else:
            roi = Decimal('0')
        
        if total_torneios > 0:
            taxa_itm = (top_5 / total_torneios) * 100
        else:
            taxa_itm = Decimal('0')
        
        pontos_totais = resultados.aggregate(Sum('pontos_finais'))['pontos_finais__sum'] or 0
        
        if total_torneios > 0:
            media_pontos = Decimal(pontos_totais) / Decimal(total_torneios)
        else:
            media_pontos = Decimal('0')
        
        stats, created = PlayerStatistics.objects.get_or_create(
            season=temporada,
            player=player,
            tenant=tenant,
            defaults={
                'total_torneios': total_torneios,
                'torneios_com_resultado': total_torneios,
                'vitórias': vitoria,
                'top_3': top_3,
                'top_5': top_5,
                'total_buyin': total_buyin,
                'total_premio': total_premio,
                'roi': roi,
                'taxa_itm': taxa_itm,
                'pontos_totais': pontos_totais,
                'media_pontos': media_pontos,
            }
        )
        
        if not created:
            stats.total_torneios = total_torneios
            stats.vitórias = vitoria
            stats.top_3 = top_3
            stats.top_5 = top_5
            stats.total_buyin = total_buyin
            stats.total_premio = total_premio
            stats.roi = roi
            stats.taxa_itm = taxa_itm
            stats.pontos_totais = pontos_totais
            stats.media_pontos = media_pontos
            stats.save()

if __name__ == '__main__':
    populate_veris_data()
