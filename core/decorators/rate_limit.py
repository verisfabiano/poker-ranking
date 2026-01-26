"""
Rate Limiting para Autenticação
Protege contra brute force em login
"""
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta


class RateLimitExceeded(Exception):
    """Exceção quando rate limit é excedido"""
    pass


def get_client_ip(request):
    """Obter IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rate_limit(max_attempts=5, window_minutes=1, key_prefix='rate_limit'):
    """
    Decorator para rate limiting
    
    Args:
        max_attempts: Número máximo de tentativas permitidas
        window_minutes: Janela de tempo em minutos
        key_prefix: Prefixo da chave no cache
    
    Uso:
        @rate_limit(max_attempts=5, window_minutes=1)
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Só aplica rate limit em POST
            if request.method != 'POST':
                return view_func(request, *args, **kwargs)
            
            # Obter IP do cliente
            client_ip = get_client_ip(request)
            cache_key = f'{key_prefix}:{client_ip}:{view_func.__name__}'
            
            # Obter tentativas atuais
            attempts = cache.get(cache_key, 0)
            
            # Verificar se excedeu limite
            if attempts >= max_attempts:
                remaining_time = cache.ttl(cache_key)
                
                # Renderizar página de erro com rate limit
                return HttpResponse(
                    f'''
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Muitas Tentativas</title>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                min-height: 100vh;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin: 0;
                                padding: 20px;
                            }}
                            .container {{
                                background: white;
                                border-radius: 8px;
                                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                                max-width: 400px;
                                padding: 40px;
                                text-align: center;
                            }}
                            h1 {{
                                color: #fa5252;
                                font-size: 24px;
                                margin-bottom: 20px;
                            }}
                            p {{
                                color: #666;
                                margin-bottom: 15px;
                                line-height: 1.6;
                            }}
                            .info {{
                                background: #fff3bf;
                                border-left: 4px solid #ffd43b;
                                padding: 12px;
                                margin: 20px 0;
                                border-radius: 4px;
                                text-align: left;
                                font-size: 14px;
                                color: #333;
                            }}
                            .timer {{
                                font-size: 32px;
                                font-weight: bold;
                                color: #667eea;
                                margin: 20px 0;
                            }}
                            a {{
                                color: #667eea;
                                text-decoration: none;
                                font-weight: bold;
                            }}
                            a:hover {{
                                text-decoration: underline;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>⏱️ Muitas Tentativas</h1>
                            <p>Você excedeu o limite de tentativas de login.</p>
                            
                            <div class="info">
                                <strong>Máximo de tentativas:</strong> {max_attempts} por minuto<br>
                                <strong>Tente novamente em:</strong> <span class="timer">{remaining_time if remaining_time else window_minutes}s</span>
                            </div>
                            
                            <p>Por questões de segurança, sua conexão foi temporariamente bloqueada.</p>
                            
                            <p>
                                <a href="/">← Voltar</a> | 
                                <a href="/auth/forgot-password/">Esqueci a senha</a>
                            </p>
                        </div>
                    </body>
                    </html>
                    ''',
                    status=429,
                    content_type='text/html; charset=utf-8'
                )
            
            # Incrementar tentativas
            attempts += 1
            cache.set(cache_key, attempts, window_minutes * 60)
            
            # Chamar view
            response = view_func(request, *args, **kwargs)
            
            # Se sucesso (redirect ou não erro), limpar cache
            if isinstance(response, HttpResponse) and response.status_code < 400:
                cache.delete(cache_key)
            
            return response
        
        return wrapper
    return decorator


def rate_limit_by_email(max_attempts=5, window_minutes=1):
    """
    Rate limit por email (ao invés de IP)
    Útil quando user tenta múltiplos emails
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method != 'POST':
                return view_func(request, *args, **kwargs)
            
            # Obter email do POST
            email = request.POST.get('email', '').strip().lower()
            if not email:
                return view_func(request, *args, **kwargs)
            
            cache_key = f'rate_limit_email:{email}:{view_func.__name__}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                remaining_time = cache.ttl(cache_key)
                return HttpResponse(
                    f'Muitas tentativas com este email. Tente novamente em {remaining_time} segundos.',
                    status=429
                )
            
            attempts += 1
            cache.set(cache_key, attempts, window_minutes * 60)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
