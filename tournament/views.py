from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import logout as django_logout
from django.core.exceptions import PermissionDenied

from tournament.models import (
    ChampionshipStanding,
    Match,
    Event,
    BridgeGroupResult,
    Team,
    SwimmingResult,
    Player
)
from tournament.engine import update_championship, is_placeholder_match

# ============================
# Gateway & Authentication
# ============================

def login_selection(request):
    """The central portal featuring MGCL 2026 branding."""
    event = Event.objects.first()
    return render(request, "tournament/login_selection.html", {"event": event})

def custom_logout(request):
    """Logs out and redirects to the Selection Gateway instead of standard login."""
    django_logout(request)
    return redirect('login_selection')

# ============================
# Leaderboard & Data
# ============================

def leaderboard(request):
    standings_a = ChampionshipStanding.objects.filter(team__pool="A").select_related('team').order_by(
        "-total_points", "-gold", "-silver", "-bronze"
    )
    standings_b = ChampionshipStanding.objects.filter(team__pool="B").select_related('team').order_by(
        "-total_points", "-gold", "-silver", "-bronze"
    )
    return render(request, "tournament/leaderboard.html", {
        "standings_a": standings_a,
        "standings_b": standings_b
    })

def leaderboard_data(request):
    standings = ChampionshipStanding.objects.order_by("-total_points", "-gold", "-silver", "-bronze")
    data = []
    for i, s in enumerate(standings, start=1):
        data.append({
            "rank": i, "team": s.team.name, "points": s.total_points, 
            "gold": s.gold, "silver": s.silver, "bronze": s.bronze
        })
    return JsonResponse(data, safe=False)

# ============================
# Fixtures & Big Screen
# ============================

def fixtures(request):
    events = Event.objects.prefetch_related("matches").order_by("sport__name", "event_id")
    bridge_rankings = {}
    for r in BridgeGroupResult.objects.select_related("event", "first", "second", "third"):
        bridge_rankings.setdefault(r.event_id, {})[r.group] = r
    return render(request, "tournament/fixtures.html", {"events": events, "bridge_rankings": bridge_rankings})

def big_screen(request):
    standings_a = ChampionshipStanding.objects.filter(team__pool="A").order_by("-total_points", "-gold")
    standings_b = ChampionshipStanding.objects.filter(team__pool="B").order_by("-total_points", "-gold")
    upcoming = Match.objects.filter(completed=False).select_related('team1', 'team2', 'event', 'event__sport').order_by('date', 'time')[:6]
    recent = Match.objects.filter(completed=True).select_related('team1', 'team2', 'event', 'event__sport').order_by('-date', '-time')[:6]
    return render(request, "tournament/big_screen.html", {"standings_a": standings_a, "standings_b": standings_b, "upcoming": upcoming, "recent": recent})

# ============================
# Captain's Portal
# ============================

@login_required
def captain_dashboard(request):
    try:
        my_team = request.user.team_profile
    except AttributeError:
        return render(request, "tournament/captain_error.html", {"message": "You are not linked to a team."})
    my_matches = Match.objects.filter((Q(team1=my_team) | Q(team2=my_team)), completed=False).select_related('event', 'event__sport').order_by('date', 'time')
    return render(request, "tournament/captain_dashboard.html", {"team": my_team, "matches": my_matches})

@login_required
def select_squad(request, match_id):
    """Handles Official Players + Guest Players with Auto-Update and Validation."""
    match = get_object_or_404(Match, id=match_id)
    my_team = request.user.team_profile
    if match.team1 != my_team and match.team2 != my_team:
        return redirect('captain_dashboard')
    
    sport_name = match.event.sport.name
    roster = Player.objects.filter(team=my_team).filter(Q(sport_label__icontains=sport_name) | Q(sport_label__icontains="All"))
    
    # Calculate required count (e.g., 2 for doubles/bridge, 1 for singles)
    req_count = 2 if "double" in match.event.name.lower() or "bridge" in sport_name.lower() else 1

    if request.method == "POST":
        selected_ids = request.POST.getlist('players')
        guest_name = request.POST.get('guest_name', '').strip()
        
        # --- VALIDATION CHECK ---
        total_selected = len(selected_ids) + (1 if guest_name else 0)
        
        if total_selected > req_count:
            messages.error(request, f"Too many players! This match only requires {req_count} player(s).")
            current_squad = match.team1_players if match.team1 == my_team else match.team2_players
            return render(request, "tournament/select_squad.html", {
                "match": match, "roster": roster, "req_count": req_count, "current_squad": current_squad or ""
            })

        # Process names
        selected_objs = roster.filter(id__in=selected_ids)
        player_names = [p.name for p in selected_objs]
        if guest_name:
            player_names.append(guest_name)
        
        final_squad = " & ".join(player_names)
        if match.team1 == my_team: match.team1_players = final_squad
        else: match.team2_players = final_squad
        match.save()

        # --- AUTO-UPDATE LOGIC ---
        if not guest_name and len(selected_ids) == (roster.count() / 2):
            other_match = Match.objects.filter(event=match.event, completed=False).filter(
                Q(team1=my_team) | Q(team2=my_team)
            ).exclude(id=match.id).first()
            
            if other_match:
                remaining_players = roster.exclude(id__in=selected_ids)
                rem_squad = " & ".join([p.name for p in remaining_players])
                if other_match.team1 == my_team: other_match.team1_players = rem_squad
                else: other_match.team2_players = rem_squad
                other_match.save()
                messages.info(request, "Other match squad updated automatically.")

        messages.success(request, f"Squad saved for {match.event.name}!")
        return redirect('captain_dashboard')

    current_squad = match.team1_players if match.team1 == my_team else match.team2_players
    return render(request, "tournament/select_squad.html", {
        "match": match, "roster": roster, "req_count": req_count, "current_squad": current_squad or ""
    })

# ============================
# Score Entry (Staff Only)
# ============================

@login_required 
def score_entry(request, match_id):
    if not request.user.is_staff:
        raise PermissionDenied("Unauthorized Access.")

    match = get_object_or_404(Match, id=match_id)
    sport_name = match.event.sport.name.lower()
    rule_lower = (match.opponent_rule or "").lower()

    if "swimming" in sport_name: return swimming_score_entry(request, match)
    if "bridge" in sport_name and "all teams" in rule_lower: return bridge_group_score_entry(request, match)

    if match.team1 and match.team2:
        team1_name, team2_name = match.team1.name, match.team2.name
    elif "vs" in rule_lower:
        parts = match.opponent_rule.split("vs")
        team1_name, team2_name = parts[0].strip(), parts[1].strip()
    else:
        return render(request, "tournament/placeholder_match.html", {"match": match, "reason": "Waiting for results."})

    if request.method == "POST":
        try:
            s1, s2 = int(request.POST.get("team1_score")), int(request.POST.get("team2_score"))
            match.team1_score, match.team2_score = s1, s2
            match.completed = True
            match.winner = team1_name if s1 > s2 else team2_name
            match.save()
            update_championship(match.event)
            return redirect(reverse("fixtures") + f"#match-{match.id}")
        except:
            return render(request, "tournament/score_entry.html", {"match": match, "team1_name": team1_name, "team2_name": team2_name, "error": "Invalid Score."})

    return render(request, "tournament/score_entry.html", {"match": match, "team1_name": team1_name, "team2_name": team2_name})

def bridge_group_score_entry(request, match):
    teams = Team.objects.filter(code__in=["T1", "T2", "T3"]) if match.group == "A" else Team.objects.filter(code__in=["T4", "T5", "T6"])
    initial_raw_scores = {}
    existing_res = BridgeGroupResult.objects.filter(event=match.event, group=match.group).first()
    if existing_res:
        initial_raw_scores = {existing_res.first.id: existing_res.first_score, existing_res.second.id: existing_res.second_score, existing_res.third.id: existing_res.third_score}

    if request.method == "POST":
        scores_data = []
        for team in teams:
            val = request.POST.get(f"score_{team.id}")
            if val: scores_data.append((team, float(val)))
        scores_data.sort(key=lambda x: x[1], reverse=True)
        if len(scores_data) >= 3:
            BridgeGroupResult.objects.update_or_create(event=match.event, group=match.group, defaults={"first": scores_data[0][0], "second": scores_data[1][0], "third": scores_data[2][0], "first_score": scores_data[0][1], "second_score": scores_data[1][1], "third_score": scores_data[2][1]})
            match.completed, match.winner = True, f"1st: {scores_data[0][0].name}"
            match.save()
            update_championship(match.event)
            return redirect(reverse("fixtures") + f"#match-{match.id}")

    return render(request, "tournament/bridge_score_entry.html", {"match": match, "teams": teams, "initial_raw_scores": initial_raw_scores})

def swimming_score_entry(request, match):
    all_teams = Team.objects.all().order_by("name")
    if request.method == "POST":
        res_teams = [Team.objects.get(id=request.POST.get(f"rank_{i}")) for i in range(1, 7)]
        SwimmingResult.objects.update_or_create(event=match.event, defaults={"first": res_teams[0], "second": res_teams[1], "third": res_teams[2], "fourth": res_teams[3], "fifth": res_teams[4], "sixth": res_teams[5]})
        match.completed, match.winner = True, f"Gold: {res_teams[0].name}"
        match.save()
        update_championship(match.event)
        return redirect(reverse("fixtures") + f"#match-{match.id}")
    return render(request, "tournament/swimming_score_entry.html", {"match": match, "teams": all_teams, "existing": SwimmingResult.objects.filter(event=match.event).first()})