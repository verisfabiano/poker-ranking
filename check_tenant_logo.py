#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Tenant, TenantUser
from django.contrib.auth.models import User

user = User.objects.get(username='veris')
tenant_user = TenantUser.objects.filter(user=user).first()

if tenant_user:
    tenant = tenant_user.tenant
    print(f"Tenant: {tenant.nome}")
    print(f"Logo: {tenant.logo}")
    if tenant.logo:
        print(f"Logo URL: {tenant.logo.url}")
    else:
        print("Logo é None")
