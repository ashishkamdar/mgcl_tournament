from django.db import models


class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")

    def __str__(self):
        return self.name


class Event(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="events")
    event_id = models.IntegerField()
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.sport} | {self.name}"


class Match(models.Model):
    GROUP_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("A&B", "A & B"),
    ]

    TYPE_CHOICES = [
        ("RR", "Round Robin"),
        ("SF1", "Semi Finals 1"),
        ("SF2", "Semi Finals 2"),
        ("P56", "5-6 Position"),
        ("P34", "3-4 Position"),
        ("F", "Finals"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="matches")
    match_no = models.IntegerField()
    group = models.CharField(max_length=3, choices=GROUP_CHOICES)
    match_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    opponent_rule = models.CharField(max_length=200)

    team1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="home_matches")
    team2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="away_matches")

    date = models.DateField()
    time = models.TimeField()

    venue_type = models.CharField(max_length=20)  # Court / Table / Lane
    venue_no = models.CharField(max_length=10)

    completed = models.BooleanField(default=False)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.event} | Match {self.match_no}"

class ChampionshipStanding(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    bronze = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team} | {self.total_points} pts"

class MatchAudit(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    changed_by = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_score1 = models.IntegerField(null=True, blank=True)
    old_score2 = models.IntegerField(null=True, blank=True)
    new_score1 = models.IntegerField(null=True, blank=True)
    new_score2 = models.IntegerField(null=True, blank=True)
