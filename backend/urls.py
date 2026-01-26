from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views.public import landing_page
from core.views import home_redirect

urlpatterns = [
    # URL base -> Landing page (sem autenticação)
    path("", landing_page, name="home"),

    # Admin padrão do Django
    path("admin/", admin.site.urls),

    # Todas as URLs da app core (ranking, torneios, login jogador, etc)
    path("", include("core.urls")),
]

# Servir media files em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
