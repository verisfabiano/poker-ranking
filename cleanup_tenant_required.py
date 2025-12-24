#!/usr/bin/env python
# -*- coding: utf-8 -*-

files_to_fix = [
    'core/views/ranking.py',
    'core/views/season.py',
    'core/views/tournament.py',
    'core/views/director.py',
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover todas as linhas que contêm @tenant_required
        lines = content.split('\n')
        new_lines = [line for line in lines if '@tenant_required' not in line]
        new_content = '\n'.join(new_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {file_path}: @tenant_required removido")
    except FileNotFoundError:
        print(f"❌ {file_path}: arquivo não encontrado")
    except Exception as e:
        print(f"❌ {file_path}: erro - {e}")

print("\n✅ Limpeza concluída!")
