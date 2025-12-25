#!/usr/bin/env python
"""
Script para exportar estruturas de blinds do banco local para um arquivo JSON
que pode ser carregado no Railway.

Uso:
    python scripts/export_blinds.py
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import BlindStructure, BlindLevel, Tenant
from django.core import serializers

def export_blinds():
    """Exporta todos os BlindStructure e BlindLevel para um arquivo JSON"""
    
    print("🎲 Exportando Estruturas de Blinds...")
    
    # Obter todos os tenants para exportar
    tenants = Tenant.objects.all()
    
    if not tenants.exists():
        print("❌ Nenhum tenant encontrado no banco de dados")
        return False
    
    print(f"📍 Tenants encontrados: {tenants.count()}")
    
    # Exportar cada tenant
    for tenant in tenants:
        print(f"\n📦 Exportando blinds do tenant: {tenant.nome}")
        
        # Filtrar blinds deste tenant
        blind_structures = BlindStructure.objects.filter(tenant=tenant)
        
        if not blind_structures.exists():
            print(f"   ⚠️  Nenhuma estrutura de blinds encontrada para {tenant.nome}")
            continue
        
        print(f"   ✅ {blind_structures.count()} estruturas encontradas")
        
        # Serializar BlindStructure e BlindLevel
        data = serializers.serialize('json', blind_structures)
        
        # Também serializar os BlindLevel associados
        blind_levels = BlindLevel.objects.filter(
            structure__in=blind_structures
        )
        
        if blind_levels.exists():
            data_json = json.loads(data)
            levels_json = json.loads(serializers.serialize('json', blind_levels))
            data_json.extend(levels_json)
            data = json.dumps(data_json, indent=2)
        
        # Salvar em arquivo
        filename = f'blinds_{tenant.slug}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)
        
        print(f"   💾 Salvo em: {filename}")
    
    print("\n✅ Exportação concluída!")
    print("\n📋 Próximos passos:")
    print("   1. Faça commit dos arquivos JSON:")
    print("      git add blinds_*.json")
    print("      git commit -m 'Add: Estruturas de blinds para migração'")
    print("   2. Push para o repositório:")
    print("      git push")
    print("   3. No Railway, carregue os dados:")
    print("      railway run python manage.py loaddata blinds_*.json")
    
    return True

if __name__ == '__main__':
    try:
        export_blinds()
    except Exception as e:
        print(f"❌ Erro ao exportar: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
