#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

# Ler o arquivo
with open('core/views/player.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover todas as linhas que contêm @tenant_required
lines = content.split('\n')
new_lines = [line for line in lines if '@tenant_required' not in line]
new_content = '\n'.join(new_lines)

# Escrever de volta
with open('core/views/player.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Removidas todas as linhas @tenant_required de core/views/player.py")
