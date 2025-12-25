from django.core.management.base import BaseCommand
from django.core.management import call_command
import glob
import os

class Command(BaseCommand):
    help = 'Carrega estruturas de blinds de arquivos JSON'

    def handle(self, *args, **options):
        self.stdout.write("🎲 Procurando arquivos de blinds...")
        
        # Procurar todos os arquivos blinds_*.json
        blind_files = glob.glob('blinds_*.json')
        
        if not blind_files:
            self.stdout.write(self.style.WARNING('❌ Nenhum arquivo blinds_*.json encontrado'))
            return
        
        self.stdout.write(f"✅ Encontrados {len(blind_files)} arquivos de blinds")
        
        for file in blind_files:
            try:
                self.stdout.write(f"\n📦 Carregando {file}...")
                call_command('loaddata', file, verbosity=1)
                self.stdout.write(self.style.SUCCESS(f'✅ {file} carregado com sucesso!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao carregar {file}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Estruturas de blinds carregadas!'))
