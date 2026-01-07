from django.db.models import Q
from .models import Match, ChampionshipStanding, Team, BridgeGroupResult, SwimmingResult

def update_championship(event):
    """Main entry point for calculations."""
    calculate_group_standings(event)
    
    sport_name = event.sport.name.lower()
    
    # --- SWIMMING UNLOCK ---
    if "swimming" in sport_name:
        unlock_swimming_finals(event)
        return

    # --- BRIDGE UNLOCK ---
    if "bridge" in sport_name:
        unlock_bridge_brackets(event)
        return
        
    update_bracket_matches(event)

def unlock_swimming_finals(event):
    """Physically assigns teams to swimming matches so they aren't 'None'."""
    swimming_matches = Match.objects.filter(event=event)
    placeholder_team = Team.objects.first()
    for m in swimming_matches:
        if m.team1 is None or m.team2 is None:
            m.team1 = placeholder_team
            m.team2 = placeholder_team
            m.save()

def unlock_bridge_brackets(event):
    """Unlocks Bridge Playoffs using BridgeGroupResult table."""
    res_a = BridgeGroupResult.objects.filter(event=event, group="A").first()
    res_b = BridgeGroupResult.objects.filter(event=event, group="B").first()

    if res_a and res_b:
        bracket = Match.objects.filter(event=event, group="A&B")
        for m in bracket:
            if m.completed: continue
            rule = (m.opponent_rule or "").lower()
            
            # Match 3: SF 1 (1st A vs 2nd B)
            if "1st of group a" in rule or "2nd of group b" in rule:
                m.team1, m.team2 = res_a.first, res_b.second
                auto_assign_squad(m)
                m.save()
            # Match 4: SF 2 (1st B vs 2nd A)
            elif "1st of group b" in rule or "2nd of group a" in rule:
                m.team1, m.team2 = res_b.first, res_a.second
                auto_assign_squad(m)
                m.save()
            # Match 5: 5-6 Position (3rd A vs 3rd B)
            elif "3rd of group a" in rule or "3rd of group b" in rule:
                m.team1, m.team2 = res_a.third, res_b.third
                auto_assign_squad(m)
                m.save()

        # Unlock Finals and 3rd Place Match (Match 6) based on Semi results
        update_bridge_playoff_advancement(event)

def update_bridge_playoff_advancement(event):
    """Specifically unlocks Match 6 (3rd Place) and Match 7 (Finals) for Bridge."""
    bracket_qs = Match.objects.filter(event=event, group="A&B")
    
    # 1. Identify completed Semi-Finals
    # We look for Match 3 and Match 4 specifically
    sf_done = bracket_qs.filter(completed=True).filter(
        Q(match_no=3) | Q(match_no=4)
    ).order_by('match_no')

    # 2. Only proceed if BOTH Semi-Finals are done
    if sf_done.count() >= 2:
        sf1 = sf_done.filter(match_no=3).first()
        sf2 = sf_done.filter(match_no=4).first()
        
        def get_w(m): return m.team1 if m.winner == m.team1.name else m.team2
        def get_l(m): return m.team2 if m.winner == m.team1.name else m.team1

        # --- UNLOCK MATCH 6 (3-4 Position / 3rd Place) ---
        # Loser of SF1 vs Loser of SF2
        m6 = bracket_qs.filter(match_no=6).first()
        if m6 and not m6.completed:
            m6.team1, m6.team2 = get_l(sf1), get_l(sf2)
            auto_assign_squad(m6) # Carry forward players even if incomplete
            m6.save()

        # --- UNLOCK MATCH 7 (Finals) ---
        # Winner of SF1 vs Winner of SF2
        m7 = bracket_qs.filter(match_no=7).first()
        if m7 and not m7.completed:
            m7.team1, m7.team2 = get_w(sf1), get_w(sf2)
            auto_assign_squad(m7) # Automatically populate squad to prevent blocking
            m7.save()
            
def calculate_group_standings(event):
    """Calculates points based on the 100/70/50/40/30/10 scale."""
    all_teams = Team.objects.all()
    for t in all_teams:
        standing, _ = ChampionshipStanding.objects.get_or_create(team=t)
        standing.total_points, standing.gold, standing.silver, standing.bronze = 0, 0, 0, 0
        standing.save()

    sport_name = event.sport.name.lower()

    if "swimming" in sport_name:
        res = SwimmingResult.objects.filter(event=event).first()
        if res:
            award_points(res.first, 100, "gold")
            award_points(res.second, 70, "silver")
            award_points(res.third, 50, "bronze")
            award_points(res.fourth, 40, "")
            award_points(res.fifth, 30, "")
            award_points(res.sixth, 10, "")
        return

    if "bridge" in sport_name:
        bridge_rankings = BridgeGroupResult.objects.filter(event=event)
        for res in bridge_rankings:
            award_points(res.first, 100, "gold")
            award_points(res.second, 70, "silver")
            award_points(res.third, 50, "bronze")
        if bridge_rankings.exists() and not Match.objects.filter(event=event, group="A&B", completed=True).exists():
            return

    bracket = Match.objects.filter(event=event, group="A&B", completed=True)
    
    # Finals (100/70 pts)
    f_match = bracket.filter(Q(match_type="F") | Q(opponent_rule__icontains="winner")).first()
    if f_match:
        win_obj = f_match.team1 if f_match.winner == f_match.team1.name else f_match.team2
        lose_obj = f_match.team2 if f_match.winner == f_match.team1.name else f_match.team1
        award_points(win_obj, 100, "gold")
        award_points(lose_obj, 70, "silver")

    # 3rd Place Match (50/40 pts) - Match 6
    p34_match = bracket.filter(Q(match_no=6) | Q(match_type="P34") | Q(opponent_rule__icontains="loser")).first()
    if p34_match:
        win_obj = p34_match.team1 if p34_match.winner == p34_match.team1.name else p34_match.team2
        lose_obj = p34_match.team2 if p34_match.winner == p34_match.team1.name else p34_match.team1
        award_points(win_obj, 50, "bronze")
        award_points(lose_obj, 40, "")

    # 5-6 Playoff (30/10 pts) - Match 5
    p56_match = bracket.filter(Q(match_no=5) | Q(match_type="P56") | Q(opponent_rule__icontains="3rd")).first()
    if p56_match:
        win_obj = p56_match.team1 if p56_match.winner == p56_match.team1.name else p56_match.team2
        lose_obj = p56_match.team2 if p56_match.winner == p56_match.team1.name else p56_match.team1
        award_points(win_obj, 30, "")
        award_points(lose_obj, 10, "")

def award_points(team, points, medal):
    if not team: return
    s, _ = ChampionshipStanding.objects.get_or_create(team=team)
    s.total_points += points
    if medal == "gold": s.gold += 1
    elif medal == "silver": s.silver += 1
    elif medal == "bronze": s.bronze += 1
    s.save()

def auto_assign_squad(match):
    """Guesses squad from previous rounds to keep the show going."""
    def get_prev(team):
        if not team: return ""
        last = Match.objects.filter(event=match.event, completed=True).filter(Q(team1=team) | Q(team2=team)).order_by('-match_no').first()
        return (last.team1_players if last.team1 == team else last.team2_players) if last else ""
    if not match.team1_players: match.team1_players = get_prev(match.team1)
    if not match.team2_players: match.team2_players = get_prev(match.team2)

def update_bracket_matches(event):
    if Match.objects.filter(event=event, group__in=["A", "B"], completed=False).exclude(team1=None).exists():
        return 
    standings_a, standings_b = get_sorted_teams(event, "A"), get_sorted_teams(event, "B")
    if len(standings_a) < 2 or len(standings_b) < 2: return
    bracket_qs = Match.objects.filter(event=event, group="A&B")
    for m in bracket_qs:
        if m.completed: continue
        rule = (m.opponent_rule or "").lower()
        if "1st of group a" in rule or "2nd of group b" in rule:
            m.team1, m.team2 = standings_a[0], standings_b[1]
            auto_assign_squad(m)
            m.save()
        elif "1st of group b" in rule or "2nd of group a" in rule:
            m.team1, m.team2 = standings_b[0], standings_a[1]
            auto_assign_squad(m)
            m.save()
        elif "3rd of group a" in rule and len(standings_a) >= 3 and len(standings_b) >= 3:
            m.team1, m.team2 = standings_a[2], standings_b[2]
            auto_assign_squad(m)
            m.save()

def get_sorted_teams(event, group):
    matches = Match.objects.filter(event=event, group=group, completed=True)
    teams = Team.objects.filter(pool=group)
    stats = {t.id: {'wins': 0, 'diff': 0, 'obj': t} for t in teams}
    for m in matches:
        if m.winner == m.team1.name: stats[m.team1.id]['wins'] += 1
        elif m.winner == m.team2.name: stats[m.team2.id]['wins'] += 1
        stats[m.team1.id]['diff'] += (m.team1_score - m.team2_score)
        stats[m.team2.id]['diff'] += (m.team2_score - m.team1_score)
    return [i['obj'] for i in sorted(stats.values(), key=lambda x: (x['wins'], x['diff']), reverse=True)]

def is_placeholder_match(match):
    if "swimming" in match.event.sport.name.lower(): return False
    return match.team1 is None or match.team2 is None