#!/usr/bin/env python
"""
Script para resetar a senha do usuário veris
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

# Buscar o usuário veris
try:
    user = User.objects.get(username='veris')
    # Definir a senha
    user.set_password('veris123')
    user.save()
    print(f"✅ Senha do usuário 'veris' alterada para 'veris123'")
except User.DoesNotExist:
    print("❌ Usuário 'veris' não encontrado")
