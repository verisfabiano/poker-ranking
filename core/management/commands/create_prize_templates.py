# core/management/commands/create_prize_templates.py

from django.core.management.base import BaseCommand
from core.models import Tenant, PrizeTemplate
import json


class Command(BaseCommand):
    help = 'Cria templates padrão de premiação para todos os tenants'

    def handle(self, *args, **options):
        # Definir templates padrão
        templates_data = [
            # ========== TOP 3 CLÁSSICO ==========
            {
                'nome': 'Top 3 - Clássico (50/30/20)',
                'descricao': 'Estrutura clássica: 50% para 1º, 30% para 2º, 20% para 3º. Ideal para 18-23 jogadores.',
                'modo': 'PERCENTUAL',
                'itm_count': 3,
                'data': [
                    {'position': 1, 'percentage': 50.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 30.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 20.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 4 BALANCEADO ==========
            {
                'nome': 'Top 4 - Balanceado (42/28/18/12)',
                'descricao': 'Estrutura para 24-27 jogadores. Garante que 4º lugar recebe "a salva".',
                'modo': 'PERCENTUAL',
                'itm_count': 4,
                'data': [
                    {'position': 1, 'percentage': 42.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 28.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 18.00, 'valor_fixo': None},
                    {'position': 4, 'percentage': 12.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 4 AGRESSIVO ==========
            {
                'nome': 'Top 4 - Agressivo (45/25/15/15)',
                'descricao': 'Variante mais agressiva do Top 4. 1º lugar leva mais, 3º e 4º iguais.',
                'modo': 'PERCENTUAL',
                'itm_count': 4,
                'data': [
                    {'position': 1, 'percentage': 45.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 25.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 15.00, 'valor_fixo': None},
                    {'position': 4, 'percentage': 15.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 5 DISTRIBUÍDO ==========
            {
                'nome': 'Top 5 - Distribuído (35/23/17/13/12)',
                'descricao': 'Para 28-30 jogadores. Distribui mais equitativamente entre os premiadosideal para min-cash bem definido.',
                'modo': 'PERCENTUAL',
                'itm_count': 5,
                'data': [
                    {'position': 1, 'percentage': 35.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 23.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 17.00, 'valor_fixo': None},
                    {'position': 4, 'percentage': 13.00, 'valor_fixo': None},
                    {'position': 5, 'percentage': 12.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 6 GRANDES EVENTOS ==========
            {
                'nome': 'Top 6 - Grandes Eventos (30/20/15/12/12/11)',
                'descricao': 'Para torneios com 40+ jogadores. 15% do field premiado com distribuição progressiva.',
                'modo': 'PERCENTUAL',
                'itm_count': 6,
                'data': [
                    {'position': 1, 'percentage': 30.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 20.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 15.00, 'valor_fixo': None},
                    {'position': 4, 'percentage': 12.00, 'valor_fixo': None},
                    {'position': 5, 'percentage': 12.00, 'valor_fixo': None},
                    {'position': 6, 'percentage': 11.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 8 MEGA EVENTOS ==========
            {
                'nome': 'Top 8 - Mega Eventos (25/17/13/11/10/10/9/5)',
                'descricao': 'Para torneios com 50+ jogadores. Mesa final concentra ~60% do pote.',
                'modo': 'PERCENTUAL',
                'itm_count': 8,
                'data': [
                    {'position': 1, 'percentage': 25.00, 'valor_fixo': None},
                    {'position': 2, 'percentage': 17.00, 'valor_fixo': None},
                    {'position': 3, 'percentage': 13.00, 'valor_fixo': None},
                    {'position': 4, 'percentage': 11.00, 'valor_fixo': None},
                    {'position': 5, 'percentage': 10.00, 'valor_fixo': None},
                    {'position': 6, 'percentage': 10.00, 'valor_fixo': None},
                    {'position': 7, 'percentage': 9.00, 'valor_fixo': None},
                    {'position': 8, 'percentage': 5.00, 'valor_fixo': None},
                ]
            },
            
            # ========== TOP 3 FIXO ==========
            {
                'nome': 'Top 3 - Fixo (Customizável)',
                'descricao': 'Modo FIXO para digitar valores em reais. Ideal quando há entradas/prêmios adicionais.',
                'modo': 'FIXO',
                'itm_count': 3,
                'data': [
                    {'position': 1, 'percentage': None, 'valor_fixo': 500.00},
                    {'position': 2, 'percentage': None, 'valor_fixo': 300.00},
                    {'position': 3, 'percentage': None, 'valor_fixo': 200.00},
                ]
            },
            
            # ========== TOP 4 FIXO ==========
            {
                'nome': 'Top 4 - Fixo (Customizável)',
                'descricao': 'Modo FIXO com 4 posições. Edite os valores conforme necessário.',
                'modo': 'FIXO',
                'itm_count': 4,
                'data': [
                    {'position': 1, 'percentage': None, 'valor_fixo': 500.00},
                    {'position': 2, 'percentage': None, 'valor_fixo': 300.00},
                    {'position': 3, 'percentage': None, 'valor_fixo': 150.00},
                    {'position': 4, 'percentage': None, 'valor_fixo': 50.00},
                ]
            },
        ]
        
        # Criar templates para todos os tenants
        tenants = Tenant.objects.filter(ativo=True)
        created_count = 0
        
        for tenant in tenants:
            for template_info in templates_data:
                template, created = PrizeTemplate.objects.get_or_create(
                    tenant=tenant,
                    nome=template_info['nome'],
                    defaults={
                        'descricao': template_info['descricao'],
                        'modo': template_info['modo'],
                        'itm_count': template_info['itm_count'],
                        'data': template_info['data'],
                        'ativo': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Template criado: {tenant.nome} - {template.nome}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total de {created_count} templates criados com sucesso!')
        )
