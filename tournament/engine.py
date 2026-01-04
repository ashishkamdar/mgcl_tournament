from tournament.models import Match, Team


POINTS_TABLE = {
    1: 100,
    2: 70,
    3: 50,
    4: 40,
    5: 30,
    6: 10,
}


def compute_event_rankings(event):
    teams = list(Team.objects.all())
    stats = {t.id: {"played": 0, "won": 0} for t in teams}

    matches = Match.objects.filter(event=event, completed=True)

    for m in matches:
        if not m.team1 or not m.team2:
            continue

        t1, t2 = m.team1_id, m.team2_id
        stats[t1]["played"] += 1
        stats[t2]["played"] += 1

        if m.team1_score > m.team2_score:
            stats[t1]["won"] += 1
        else:
            stats[t2]["won"] += 1

    ranking = sorted(stats.items(), key=lambda x: x[1]["won"], reverse=True)

    final_positions = {}
    for pos, (tid, _) in enumerate(ranking, start=1):
        final_positions[tid] = pos

    return final_positions


def allocate_points(event):
    positions = compute_event_rankings(event)

    championship_points = {}
    for team_id, pos in positions.items():
        championship_points[team_id] = POINTS_TABLE[pos]

    return championship_points

from tournament.models import ChampionshipStanding

MEDAL_STRUCTURE = {
    "SINGLE": 1,
    "DOUBLE": 2,
    "BRIDGE": 4,
}


def update_championship(event, event_type):
    points = allocate_points(event)

    for team_id, pts in points.items():
        standing, _ = ChampionshipStanding.objects.get_or_create(team_id=team_id)
        standing.total_points += pts
        standing.save()

    ranked = sorted(points.items(), key=lambda x: x[1], reverse=True)

    medal_units = MEDAL_STRUCTURE[event_type]

    for i, (team_id, _) in enumerate(ranked[:3]):
        standing = ChampionshipStanding.objects.get(team_id=team_id)
        if i == 0:
            standing.gold += medal_units
        elif i == 1:
            standing.silver += medal_units
        else:
            standing.bronze += medal_units
        standing.save()
