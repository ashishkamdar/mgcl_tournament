from django.contrib import admin
from .models import (
    Sport, Team, Player, Event, Match,
    ChampionshipStanding, BridgeGroupResult, SwimmingResult
)

# ============================================
# 1. PLAYER INLINE (Inside Team Screen)
# ============================================
class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0
    min_num = 0
    can_delete = True
    verbose_name = "Team Member"
    verbose_name_plural = "Team Roster"
    # Explicitly show these fields
    fields = ('name', 'sport_label') 

# ============================================
# 2. PLAYER ADMIN (Global Search & Filter)
# ============================================
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "sport_label")
    list_filter = ("team", "sport_label") # <--- Filter by Sport here
    search_fields = ("name", "team__name", "sport_label")

# ============================================
# 3. TEAM ADMIN
# ============================================
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "owners", "pool", "get_player_count")
    list_filter = ("pool",)
    search_fields = ("name", "code", "owners")
    inlines = [PlayerInline]

    def get_player_count(self, obj):
        return obj.players.count()
    get_player_count.short_description = "Players"

# ============================================
# 4. MATCH ADMIN
# ============================================
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "event", "match_no", "group", 
        "team1", "team2", 
        "completed", "winner"
    )
    list_filter = ("event__sport", "group", "completed", "date")
    search_fields = ("event__name", "team1__name", "team2__name")
    ordering = ("event", "match_no")

    fieldsets = (
        ("Match Details", {
            "fields": ("event", "match_no", "group", "match_type", "opponent_rule")
        }),
        ("Teams & Players", {
            "fields": (
                ("team1", "team1_players"), 
                ("team2", "team2_players")
            )
        }),
        ("Scheduling", {
            "fields": (("date", "time"), ("venue_type", "venue_no"))
        }),
        ("Result", {
            "fields": ("completed", ("team1_score", "team2_score"), ("winner", "loser"))
        }),
    )

    def has_change_permission(self, request, obj=None):
        if obj and obj.event.is_locked:
            return False
        return super().has_change_permission(request, obj)

# ============================================
# 5. OTHER ADMINS
# ============================================
@admin.register(BridgeGroupResult)
class BridgeGroupResultAdmin(admin.ModelAdmin):
    list_display = ('event', 'group', 'first', 'first_score', 'second', 'second_score', 'third', 'third_score')
    list_filter = ("event", "group")

@admin.register(SwimmingResult)
class SwimmingResultAdmin(admin.ModelAdmin):
    list_display = ("event", "first", "second", "third")

@admin.register(ChampionshipStanding)
class ChampionshipStandingAdmin(admin.ModelAdmin):
    list_display = ('team', 'total_points', 'gold', 'silver', 'bronze')
    ordering = ('-total_points', '-gold')

admin.site.register(Sport)
admin.site.register(Event)