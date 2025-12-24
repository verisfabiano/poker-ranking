#!/usr/bin/env python
import os
import django
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.views.season import painel_home
from core.middleware.tenant_middleware import TenantMiddleware

# Criar um request fake
factory = RequestFactory()
request = factory.get('/painel/')

# Adicionar sessão
middleware = SessionMiddleware(lambda x: x)
middleware.process_request(request)
request.session.save()

# Adicionar usuário
user = User.objects.get(username='veris')
request.user = user

# Adicionar tenant via middleware
tenant_middleware = TenantMiddleware(lambda x: x)
tenant_middleware.process_request(request)

print(f"Request User: {request.user}")
print(f"Request Tenant: {request.tenant}")
print(f"Request Tenant Nome: {request.tenant.nome if request.tenant else 'None'}")

# Chamar a view
try:
    response = painel_home(request)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Content-Type: {response.get('Content-Type', 'N/A')}")
    
    # Verificar o conteúdo
    content = response.rendered_content if hasattr(response, 'rendered_content') else response.content
    
    # Procurar pela seção de seasons
    if b'ranking-hero' in content:
        print("\n✓ 'ranking-hero' encontrado no HTML")
    else:
        print("\n❌ 'ranking-hero' NÃO encontrado no HTML")
    
    if b'ranking-season-card' in content:
        print("✓ 'ranking-season-card' encontrado no HTML")
    else:
        print("❌ 'ranking-season-card' NÃO encontrado no HTML")
    
    # Procurar pelas seasons
    if b'Temporada Teste' in content or b'Teste 2' in content:
        print("✓ Nome de seasons encontrado no HTML")
    else:
        print("❌ Nome de seasons NÃO encontrado no HTML")
    
except Exception as e:
    print(f"❌ Erro ao chamar a view: {e}")
    import traceback
    traceback.print_exc()
