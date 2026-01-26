#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Criar novo admin se não existir
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('✅ Admin criado com sucesso!')
    print('   Usuário: admin')
    print('   Senha: admin123')
else:
    print('⚠️  Usuário "admin" já existe no sistema')

# Listar todos os usuários
print('\n📋 Usuários cadastrados:')
for user in User.objects.all():
    role = 'ADMIN' if user.is_staff else 'Jogador'
    print(f'   • {user.username} ({user.email}) - {role}')
    
print('\n✅ Pronto para acessar em http://localhost:8000')
