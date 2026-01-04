from django.shortcuts import render
from tournament.models import ChampionshipStanding, Match


def leaderboard(request):
    standings = ChampionshipStanding.objects.order_by("-total_points", "-gold", "-silver", "-bronze")
    return render(request, "tournament/leaderboard.html", {"standings": standings})


def fixtures(request):
    matches = Match.objects.order_by("date", "time")
    return render(request, "tournament/fixtures.html", {"matches": matches})
