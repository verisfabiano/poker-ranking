from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home_redirect

urlpatterns = [
    # URL base -> decide admin x jogador
    path("", home_redirect, name="home"),

    # Admin padrão do Django
    path("admin/", admin.site.urls),

    # Allauth authentication URLs
    path("accounts/", include("allauth.urls")),

    # Todas as URLs da app core (ranking, torneios, login jogador, etc)
    path("", include("core.urls")),
]

# Servir media files em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
