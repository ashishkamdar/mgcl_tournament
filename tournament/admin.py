from django.contrib import admin
from .models import Sport, Team, Player, Event, Match, ChampionshipStanding


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("event", "match_no", "group", "match_type", "team1", "team2", "date", "time", "completed")
    list_filter = ("event", "match_type", "completed")
    ordering = ("event", "match_no")
    list_editable = ("completed",)

    def has_change_permission(self, request, obj=None):
        if obj and obj.event.is_locked:
            return False
        return super().has_change_permission(request, obj)


admin.site.register(Sport)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Event)
admin.site.register(ChampionshipStanding)
