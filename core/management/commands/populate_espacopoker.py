"""
Management command para popular o tenant espacopoker com dados de teste realistas.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from core.models import (
    Tenant, TenantUser, Season, TournamentType, Player,
    Tournament, TournamentEntry, TournamentResult,
    TournamentProduct, PlayerProductPurchase, BlindStructure, BlindLevel
)


class Command(BaseCommand):
    help = 'Popula o tenant espacopoker com dados de teste realistas'

    def handle(self, *args, **options):
        self.stdout.write("🎯 Iniciando população de dados para espacopoker...\n")
        
        # 1. Criar/obter tenant
        tenant, created = Tenant.objects.get_or_create(
            slug='espacopoker',
            defaults={
                'nome': 'Espaço Poker',
                'descricao': 'Casa de poker com rankings e torneios mensais',
                'ativo': True
            }
        )
        self.stdout.write(f"✅ Tenant: {tenant.nome}" + (" (criado)" if created else " (existente)"))
        
        # 2. Criar/obter usuário admin
        admin_user, _ = User.objects.get_or_create(
            username='admin_espacopoker',
            defaults={
                'email': 'admin@espacopoker.com',
                'first_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        TenantUser.objects.get_or_create(
            user=admin_user,
            tenant=tenant,
            defaults={'role': 'admin'}
        )
        
        # 3. Criar tipo de torneio
        ttype, _ = TournamentType.objects.get_or_create(
            nome='Texas Hold\'em',
            tenant=tenant,
            defaults={
                'descricao': 'Torneio padrão de Texas Hold\'em',
                'buyin_padrao': Decimal('50.00'),
                'rake_padrao': Decimal('7.50'),
                'multiplicador_pontos': Decimal('1.00'),
                'usa_regras_padrao': True
            }
        )
        self.stdout.write(f"✅ Tipo de Torneio: {ttype.nome}")
        
        # 4. Criar estrutura de blinds
        blind_struct, _ = BlindStructure.objects.get_or_create(
            nome='Turbo 20 minutos',
            tenant=tenant,
            defaults={'descricao': 'Estrutura turbo com níveis de 20 minutos'}
        )
        
        # Criar níveis de blind
        blind_levels = [
            (1, 5, 10, 0, 20, False),
            (2, 10, 20, 0, 20, False),
            (3, 15, 30, 0, 20, False),
            (4, 25, 50, 5, 20, False),
            (5, 0, 0, 0, 15, True),  # Break
            (6, 50, 100, 10, 20, False),
            (7, 100, 200, 20, 20, False),
            (8, 150, 300, 30, 20, False),
        ]
        
        for ordem, sb, bb, ante, tempo, is_break in blind_levels:
            BlindLevel.objects.get_or_create(
                structure=blind_struct,
                ordem=ordem,
                defaults={
                    'small_blind': sb,
                    'big_blind': bb,
                    'ante': ante,
                    'tempo_minutos': tempo,
                    'is_break': is_break,
                    'tenant': tenant
                }
            )
        self.stdout.write(f"✅ Estrutura de Blinds: {blind_struct.nome} ({len(blind_levels)} níveis)")
        
        # 5. Criar temporada
        season, _ = Season.objects.get_or_create(
            nome='Dezembro 2025',
            tenant=tenant,
            defaults={
                'data_inicio': datetime.now().date(),
                'data_fim': (datetime.now() + timedelta(days=30)).date(),
                'ativo': True,
                'tipo_calculo': 'FIXO',
                'pts_1lugar': 14,
                'pts_2lugar': 11,
                'pts_3lugar': 8,
                'pts_4lugar': 6,
                'pts_5lugar': 4,
                'pts_6lugar': 2,
                'pts_7lugar': 1,
                'pts_8lugar': 1,
                'pts_9lugar': 1,
                'pts_10lugar': 1,
            }
        )
        self.stdout.write(f"✅ Temporada: {season.nome}")
        
        # 6. Criar jogadores
        nomes_jogadores = [
            'João Silva', 'Maria Santos', 'Pedro Oliveira', 'Ana Costa',
            'Carlos Souza', 'Fernanda Lima', 'Roberto Alves', 'Juliana Martins',
            'Lucas Pereira', 'Amanda Rocha', 'Felipe Gomes', 'Beatriz Neves',
            'Marcelo Dias', 'Gabriela Ribeiro', 'Thiago Barbosa'
        ]
        
        players = []
        for nome in nomes_jogadores:
            player, _ = Player.objects.get_or_create(
                nome=nome,
                tenant=tenant,
                defaults={
                    'apelido': nome.split()[0].lower(),
                    'status': 'ATIVO',
                    'email': f"{nome.lower().replace(' ', '.')}@email.com",
                    'ativo': True
                }
            )
            players.append(player)
        
        self.stdout.write(f"✅ Jogadores criados: {len(players)}")
        
        # 7. Criar produtos com configuração de premiação
        products_config = [
            {
                'nome': 'Jack Pot',
                'descricao': 'Participação no Jack Pot (OPCIONAL)',
                'valor': Decimal('50.00'),
                'entra_em_premiacao': False,
            },
            {
                'nome': 'Staff',
                'descricao': 'Taxa de Staff/Dealer (OBRIGATÓRIO)',
                'valor': Decimal('30.00'),
                'entra_em_premiacao': False,
            },
            {
                'nome': 'Bounty',
                'descricao': 'Prêmio Bounty (OPCIONAL)',
                'valor': Decimal('25.00'),
                'entra_em_premiacao': False,
            },
            {
                'nome': 'Rebuy',
                'descricao': 'Compra adicional de fichas',
                'valor': Decimal('50.00'),
                'entra_em_premiacao': True,
            },
            {
                'nome': 'Add-on',
                'descricao': 'Compra adicional de fichas no intervalo final',
                'valor': Decimal('50.00'),
                'entra_em_premiacao': True,
            },
        ]
        
        products = {}
        for pconfig in products_config:
            product, _ = TournamentProduct.objects.get_or_create(
                nome=pconfig['nome'],
                tenant=tenant,
                defaults={
                    'descricao': pconfig['descricao'],
                    'valor': pconfig['valor'],
                    'entra_em_premiacao': pconfig['entra_em_premiacao']
                }
            )
            products[pconfig['nome']] = product
        
        self.stdout.write(f"✅ Produtos criados: {len(products_config)}")
        for nome, produto in products.items():
            status = "💰 Entra em Premiação" if produto.entra_em_premiacao else "🎯 Não entra"
            self.stdout.write(f"   • {nome}: {status}")
        
        # 8. Criar torneios encerrados com dados realistas
        tournaments_data = [
            {
                'nome': 'Torneio 15/12 - Noite',
                'data': datetime.now() - timedelta(days=2),
                'buyin': Decimal('100.00'),
                'num_players': 12,
                'rebuys_count': 3,
                'addons_count': 2,
                'permite_rebuy': True,
                'permite_addon': True,
            },
            {
                'nome': 'Torneio 14/12 - Tarde',
                'data': datetime.now() - timedelta(days=3),
                'buyin': Decimal('50.00'),
                'num_players': 15,
                'rebuys_count': 5,
                'addons_count': 4,
                'permite_rebuy': True,
                'permite_addon': True,
            },
            {
                'nome': 'Torneio 13/12 - Noite',
                'data': datetime.now() - timedelta(days=4),
                'buyin': Decimal('75.00'),
                'num_players': 10,
                'rebuys_count': 2,
                'addons_count': 1,
                'permite_rebuy': True,
                'permite_addon': False,
            },
            {
                'nome': 'Torneio 12/12 - Manhã',
                'data': datetime.now() - timedelta(days=5),
                'buyin': Decimal('30.00'),
                'num_players': 18,
                'rebuys_count': 4,
                'addons_count': 3,
                'permite_rebuy': True,
                'permite_addon': True,
            },
        ]
        
        for tdata in tournaments_data:
            # Calcular rake de 15%
            rake_valor = (tdata['buyin'] * Decimal('0.15')).quantize(Decimal('0.01'))
            
            tournament, _ = Tournament.objects.get_or_create(
                nome=tdata['nome'],
                tenant=tenant,
                defaults={
                    'season': season,
                    'tipo': ttype,
                    'blind_structure': blind_struct,
                    'data': tdata['data'],
                    'status': 'ENCERRADO',
                    'buyin': tdata['buyin'],
                    'rake_valor': rake_valor,
                    'rake_type': 'FIXO',
                    'rake_percentual': Decimal('0.00'),
                    'permite_rebuy': tdata['permite_rebuy'],
                    'rebuy_valor': Decimal('50.00') if tdata['permite_rebuy'] else Decimal('0'),
                    'rebuy_rake_valor': Decimal('7.50') if tdata['permite_rebuy'] else Decimal('0'),
                    'rebuy_rake_type': 'FIXO',
                    'permite_addon': tdata['permite_addon'],
                    'addon_valor': Decimal('50.00') if tdata['permite_addon'] else Decimal('0'),
                    'addon_rake_valor': Decimal('7.50') if tdata['permite_addon'] else Decimal('0'),
                    'addon_rake_type': 'FIXO',
                }
            )
            
            self.stdout.write(f"\n📌 Torneio: {tournament.nome}")
            self.stdout.write(f"   Buy-in: R${tdata['buyin']} | Rake: 15% (R${rake_valor})")
            
            # Adicionar entradas de jogadores
            selected_players = players[:tdata['num_players']]
            
            for idx, player in enumerate(selected_players):
                entry, _ = TournamentEntry.objects.get_or_create(
                    tournament=tournament,
                    player=player,
                    defaults={
                        'tenant': tenant,
                        'confirmou_presenca': True,
                        'confirmado_pelo_admin': True,
                        'data_inscricao': tdata['data'] - timedelta(hours=1),
                        'pontos_participacao': 1,
                    }
                )
            
            self.stdout.write(f"   ✅ {tdata['num_players']} entradas")
            
            # Adicionar rebuys
            for i in range(tdata['rebuys_count']):
                player = selected_players[i % len(selected_players)]
                PlayerProductPurchase.objects.get_or_create(
                    tournament=tournament,
                    player=player,
                    product=products['Rebuy'],
                    defaults={
                        'tenant': tenant,
                        'quantidade': 1,
                        'valor_pago': Decimal('50.00')
                    }
                )
            self.stdout.write(f"   ✅ {tdata['rebuys_count']} rebuys")
            
            # Adicionar add-ons
            for i in range(tdata['addons_count']):
                player = selected_players[(i + tdata['rebuys_count']) % len(selected_players)]
                PlayerProductPurchase.objects.get_or_create(
                    tournament=tournament,
                    player=player,
                    product=products['Add-on'],
                    defaults={
                        'tenant': tenant,
                        'quantidade': 1,
                        'valor_pago': Decimal('50.00')
                    }
                )
            self.stdout.write(f"   ✅ {tdata['addons_count']} add-ons")
            
            # Criar resultados (prêmios pagos)
            # Simulando pagamento de prêmios (50% da receita bruta como prize pool)
            receita_bruta = (tdata['num_players'] * tdata['buyin']) + \
                           (tdata['rebuys_count'] * Decimal('50.00')) + \
                           (tdata['addons_count'] * Decimal('50.00'))
            
            rake_total = receita_bruta * Decimal('0.15')
            prize_pool = receita_bruta - rake_total
            
            # Distribuir prêmios aos top 4
            premios = [
                Decimal(prize_pool * Decimal('0.50')),  # 1º: 50%
                Decimal(prize_pool * Decimal('0.25')),  # 2º: 25%
                Decimal(prize_pool * Decimal('0.15')),  # 3º: 15%
                Decimal(prize_pool * Decimal('0.10')),  # 4º: 10%
            ]
            
            tabela_pontos = season.get_tabela_pontos_fixos()
            
            for pos in range(min(4, len(selected_players))):
                player = selected_players[pos]
                pontos = tabela_pontos.get(pos + 1, 0)
                
                result, _ = TournamentResult.objects.get_or_create(
                    tournament=tournament,
                    player=player,
                    defaults={
                        'tenant': tenant,
                        'posicao': pos + 1,
                        'pontos_base': pontos,
                        'pontos_bonus': 0,
                        'pontos_ajuste_deal': 0,
                        'pontos_finais': pontos,
                        'premiacao_recebida': premios[pos]
                    }
                )
            
            self.stdout.write(f"   ✅ Resultados: {min(4, len(selected_players))} posições com prêmios")
            self.stdout.write(f"   💰 Prize Pool: R${prize_pool:.2f}")
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✨ População completa! {len(tournaments_data)} torneios criados com sucesso."
        ))
