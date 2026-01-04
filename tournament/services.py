from .models import Match, Standing


def recalculate_group_standings(group):
    standings = {s.team_id: s for s in group.standings.all()}

    # Reset
    for s in standings.values():
        s.played = 0
        s.won = 0
        s.lost = 0
        s.points = 0
        s.score_diff = 0

    matches = Match.objects.filter(
        event=group.event,
        match_type="GROUP",
        completed=True,
        team1__group=group,
        team2__group=group
    )

    for match in matches:
        t1 = standings[match.team1_id]
        t2 = standings[match.team2_id]

        t1.played += 1
        t2.played += 1

        t1.score_diff += match.team1_score - match.team2_score
        t2.score_diff += match.team2_score - match.team1_score

        if match.team1_score > match.team2_score:
            t1.won += 1
            t2.lost += 1
            t1.points += 2
        else:
            t2.won += 1
            t1.lost += 1
            t2.points += 2

    for s in standings.values():
        s.save()
