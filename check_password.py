#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

u = User.objects.get(username='veris')
print(f'Username: {u.username}')
print(f'Password hash starts with: {u.password[:30]}')

# Tentar verificar a senha
user = authenticate(username='veris', password='veris123')
print(f'\nAutenticado com "veris123"? {user is not None}')

# Tentar outras variações
user = authenticate(username='veris@veris.com', password='veris123')
print(f'Autenticado com "veris@veris.com" e "veris123"? {user is not None}')

# Tentar com email
user = authenticate(email='veris@veris.com', password='veris123')
print(f'Autenticado com email "veris@veris.com"? {user is not None}')
