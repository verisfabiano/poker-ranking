from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse


def superadmin_required(view_func):
    """
    Decorator que garante que apenas superusers possam acessar a view.
    
    Uso:
        @superadmin_required
        def superadmin_dashboard(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verifica se está autenticado
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        
        # Verifica se é superuser
        if not request.user.is_superuser:
            return redirect(reverse('home_redirect'))
        
        return view_func(request, *args, **kwargs)
    return wrapper
