from django.contrib import admin
from .models import (
    Season,
    Player,
    TournamentType,
    Tournament,
    TournamentEntry,
    TournamentResult,
)

admin.site.register(Season)
admin.site.register(Player)
admin.site.register(TournamentType)
admin.site.register(Tournament)
admin.site.register(TournamentEntry)
admin.site.register(TournamentResult)
