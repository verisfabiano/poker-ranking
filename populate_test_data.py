#!/usr/bin/env python
"""
Script para popular dados de teste no sistema de ranking de poker.
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

def criar_tenant():
    """Cria um tenant de teste se não existir"""
    tenant, created = Tenant.objects.get_or_create(
        slug='clube-teste',
        defaults={
            'nome': 'Clube Poker Teste',
            'descricao': 'Clube de teste para ranking',
            'ativo': True,
            'club_email': 'contato@clubeteste.com.br',
            'club_phone': '11999999999',
        }
    )
    if created:
        print(f"✓ Tenant criado: {tenant.nome}")
    else:
        print(f"✓ Tenant existente: {tenant.nome}")
    return tenant

def criar_jogadores(tenant):
    """Cria 15 jogadores de teste"""
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
            defaults={
                'apelido': apelido,
                'tenant': tenant,
                'status': 'ATIVO',
                'ativo': True,
            }
        )
        jogadores.append(player)
        status = "✓ Criado" if created else "✓ Existente"
        print(f"  {status}: {nome} ({apelido})")
    
    print(f"\n✓ Total de jogadores: {len(jogadores)}\n")
    return jogadores

def criar_tipo_torneio(tenant):
    """Cria um tipo de torneio padrão"""
    tipo, created = TournamentType.objects.get_or_create(
        nome='Texas Hold\'em',
        tenant=tenant,
        defaults={
            'descricao': 'Torneio clássico de Texas Hold\'em',
            'buyin_padrao': Decimal('100.00'),
            'rake_padrao': Decimal('10.00'),
            'multiplicador_pontos': Decimal('1.00'),
        }
    )
    if created:
        print(f"✓ Tipo de torneio criado: {tipo.nome}")
    else:
        print(f"✓ Tipo de torneio existente: {tipo.nome}")
    return tipo

def criar_estrutura_blinds(tenant):
    """Cria uma estrutura de blinds padrão"""
    structure, created = BlindStructure.objects.get_or_create(
        nome='Padrão 20 minutos',
        tenant=tenant,
        defaults={
            'descricao': 'Estrutura padrão com blinds de 20 em 20 minutos',
        }
    )
    
    if created:
        # Criar níveis
        blind_levels = [
            (1, 10, 20, 0, 20, False),
            (2, 20, 40, 0, 20, False),
            (3, 50, 100, 10, 20, False),
            (4, 100, 200, 20, 20, False),
            (5, 200, 400, 40, 20, False),
            (6, 0, 0, 0, 15, True),  # Break
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
        print(f"✓ Estrutura de blinds criada: {structure.nome}")
    else:
        print(f"✓ Estrutura de blinds existente: {structure.nome}")
    
    return structure

def criar_temporadas(tenant):
    """Cria 2 temporadas de teste"""
    temporadas = []
    
    # Temporada 1 - 2024
    season1, created = Season.objects.get_or_create(
        nome='Temporada 2024',
        tenant=tenant,
        defaults={
            'data_inicio': date(2024, 1, 1),
            'data_fim': date(2024, 12, 31),
            'ativo': True,
            'tipo_calculo': 'DINAMICO',
        }
    )
    temporadas.append(season1)
    status = "✓ Criada" if created else "✓ Existente"
    print(f"{status}: Temporada 2024")
    
    # Temporada 2 - 2025
    season2, created = Season.objects.get_or_create(
        nome='Temporada 2025',
        tenant=tenant,
        defaults={
            'data_inicio': date(2025, 1, 1),
            'data_fim': date(2025, 12, 31),
            'ativo': True,
            'tipo_calculo': 'DINAMICO',
        }
    )
    temporadas.append(season2)
    status = "✓ Criada" if created else "✓ Existente"
    print(f"{status}: Temporada 2025")
    
    print(f"\n✓ Total de temporadas: {len(temporadas)}\n")
    return temporadas

def criar_torneios(tenant, temporada, tipo_torneio, estrutura_blinds):
    """Cria 5 torneios para uma temporada"""
    torneios = []
    
    # Datas para os torneios (espaçados em uma semana)
    data_base = timezone.now().replace(hour=20, minute=0, second=0, microsecond=0)
    
    nomes_torneios = [
        'Semanal #1 - Quarta',
        'Semanal #2 - Sexta',
        'Especial Sábado',
        'Torneio da Casa',
        'Mega Torneio',
    ]
    
    for i, nome in enumerate(nomes_torneios):
        # Variar datas
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
                'blind_structure': estrutura_blinds,
                'total_jogadores': 0,  # Será atualizado
            }
        )
        torneios.append(torneio)
        status = "✓ Criado" if created else "✓ Existente"
        print(f"  {status}: {nome} ({data.strftime('%d/%m/%Y')})")
    
    print(f"\n✓ Total de torneios: {len(torneios)}\n")
    return torneios

def criar_inscritos_e_resultados(tenant, torneios, jogadores):
    """
    Cria inscrições e resultados para os torneios.
    Cada torneio tem um número variável de inscritos (8-15).
    """
    print("Criando inscrições e resultados...\n")
    
    for torneio in torneios:
        # Selecionar jogadores aleatoriamente (8-15 inscritos)
        num_inscritos = random.randint(8, 15)
        inscritos = random.sample(jogadores, min(num_inscritos, len(jogadores)))
        
        # Registrar incrições
        for jogador in inscritos:
            entry, created = TournamentEntry.objects.get_or_create(
                tournament=torneio,
                player=jogador,
                tenant=tenant,
                defaults={
                    'confirmou_presenca': True,
                    'confirmado_pelo_admin': True,
                }
            )
            
            # Adicionar alguns rebuys e addons aleatoriamente
            if random.random() < 0.4:  # 40% dos jogadores fazem rebuy
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
            
            if random.random() < 0.3:  # 30% dos jogadores fazem addon
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
        
        # Atualizar total de jogadores
        torneio.total_jogadores = len(inscritos)
        torneio.save()
        
        # Criar resultados (posições de 1 a N)
        print(f"  Torneio: {torneio.nome}")
        posicoes = list(range(1, len(inscritos) + 1))
        random.shuffle(posicoes)
        
        for idx, jogador in enumerate(inscritos):
            posicao = posicoes[idx]
            
            # Calcular prêmio baseado na posição
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
            
            resultado, created = TournamentResult.objects.get_or_create(
                tournament=torneio,
                player=jogador,
                tenant=tenant,
                defaults={
                    'posicao': posicao,
                    'pontos_base': 0,  # Será calculado
                    'premiacao_recebida': premiacao,
                }
            )
            
            if created:
                # Calcular pontos
                resultado.calcular_pontos()
                resultado.save()
        
        print(f"    ✓ {len(inscritos)} jogadores inscritos e com resultados\n")

def recalcular_estatisticas(temporada, tenant):
    """
    Recalcula as estatísticas dos jogadores para a temporada.
    """
    print("Recalculando estatísticas dos jogadores...\n")
    
    from django.db.models import Sum, Count, Q
    
    # Obter todos os jogadores com resultados nesta temporada
    resultados = TournamentResult.objects.filter(
        tournament__season=temporada,
        tournament__tenant=tenant,
    ).select_related('player', 'tournament')
    
    jogadores_ids = resultados.values_list('player_id', flat=True).distinct()
    
    for player_id in jogadores_ids:
        player = Player.objects.get(id=player_id)
        resultados_player = TournamentResult.objects.filter(
            tournament__season=temporada,
            tournament__tenant=tenant,
            player=player,
        )
        
        # Calcular estatísticas
        vitoria = resultados_player.filter(posicao=1).count()
        top_3 = resultados_player.filter(posicao__lte=3).count()
        top_5 = resultados_player.filter(posicao__lte=5).count()
        total_torneios = resultados_player.count()
        
        total_premio = resultados_player.aggregate(Sum('premiacao_recebida'))['premiacao_recebida__sum'] or Decimal('0')
        
        # Calcular buy-in total (cada inscrição = 1 buy-in + rebuys)
        total_buyin = Decimal('0')
        for resultado in resultados_player:
            torneio = resultado.tournament
            # Buy-in base
            total_buyin += Decimal(torneio.buyin)
            
            # Rebuys
            rebuys = TournamentPlayerPurchase.objects.filter(
                tournament=torneio,
                player=player,
                tipo__in=['REBUY', 'REBUY_DUPLO']
            ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
            total_buyin += Decimal(rebuys)
            
            # Add-ons
            addons = TournamentPlayerPurchase.objects.filter(
                tournament=torneio,
                player=player,
                tipo='ADDON'
            ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
            total_buyin += Decimal(addons)
        
        # ROI
        if total_buyin > 0:
            roi = ((total_premio - total_buyin) / total_buyin) * 100
        else:
            roi = Decimal('0')
        
        # Taxa ITM
        if total_torneios > 0:
            taxa_itm = (top_5 / total_torneios) * 100
        else:
            taxa_itm = Decimal('0')
        
        # Pontos totais
        pontos_totais = resultados_player.aggregate(Sum('pontos_finais'))['pontos_finais__sum'] or 0
        
        # Média de pontos
        if total_torneios > 0:
            media_pontos = Decimal(pontos_totais) / Decimal(total_torneios)
        else:
            media_pontos = Decimal('0')
        
        # Atualizar ou criar estatística
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
            stats.torneios_com_resultado = total_torneios
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

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("  POPULAÇÃO DE DADOS DE TESTE - RANKING POKER")
    print("="*60 + "\n")
    
    # 1. Criar tenant
    print("1. Criando Tenant...")
    tenant = criar_tenant()
    
    # 2. Criar estrutura de blinds
    print("\n2. Criando Estrutura de Blinds...")
    estrutura_blinds = criar_estrutura_blinds(tenant)
    
    # 3. Criar tipo de torneio
    print("\n3. Criando Tipo de Torneio...")
    tipo_torneio = criar_tipo_torneio(tenant)
    
    # 4. Criar jogadores
    print("\n4. Criando Jogadores...")
    jogadores = criar_jogadores(tenant)
    
    # 5. Criar temporadas
    print("\n5. Criando Temporadas...")
    temporadas = criar_temporadas(tenant)
    
    # 6. Para cada temporada, criar torneios
    for temporada in temporadas:
        print(f"\n6.{temporadas.index(temporada)+1} Criando Torneios para {temporada.nome}...")
        torneios = criar_torneios(tenant, temporada, tipo_torneio, estrutura_blinds)
        
        # 7. Criar inscrições e resultados
        print(f"7.{temporadas.index(temporada)+1} Criando Inscrições e Resultados...")
        criar_inscritos_e_resultados(tenant, torneios, jogadores)
        
        # 8. Recalcular estatísticas
        print(f"8.{temporadas.index(temporada)+1} Recalculando Estatísticas...")
        recalcular_estatisticas(temporada, tenant)
    
    print("\n" + "="*60)
    print("  ✓ POPULAÇÃO DE DADOS CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"\nResumo:")
    print(f"  • Tenant: {tenant.nome}")
    print(f"  • Jogadores: {len(jogadores)}")
    print(f"  • Temporadas: {len(temporadas)}")
    print(f"  • Torneios totais: {Tournament.objects.filter(tenant=tenant).count()}")
    print(f"  • Resultados totais: {TournamentResult.objects.filter(tournament__tenant=tenant).count()}")
    print(f"  • Estatísticas: {PlayerStatistics.objects.filter(tenant=tenant).count()}")
    print("\nAgora você pode acessar o ranking em: http://localhost:8000/ranking/\n")

if __name__ == '__main__':
    main()
