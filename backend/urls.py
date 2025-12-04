from django.contrib import admin
from django.urls import path, include

from core.views import home_redirect

urlpatterns = [
    # URL base -> decide admin x jogador
    path("", home_redirect, name="home"),

    # Admin padrão do Django
    path("admin/", admin.site.urls),

    # Todas as URLs da app core (ranking, torneios, login jogador, etc)
    path("", include("core.urls")),
]
