from django.db import models
from django.contrib.auth.models import User  # <--- Added Import

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Team(models.Model):
    # Link this Team to a Login Account for the Captain's Portal
    account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_profile")
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    owners = models.CharField(max_length=500, blank=True, null=True, help_text="Team Owners")
    pool = models.CharField(max_length=1, choices=[("A", "Group A"), ("B", "Group B")], default="A")
    icon = models.ImageField(upload_to='team_icons/', null=True, blank=True)

    def __str__(self): return f"{self.code} - {self.name}"

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    # NEW FIELD based on spreadsheet column D
    sport_label = models.CharField(max_length=100, blank=True, null=True, help_text="Assigned sport category from roster sheet")

    def __str__(self): 
        return f"{self.name} ({self.sport_label})" if self.sport_label else self.name

class Event(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="events")
    event_id = models.IntegerField()
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='event_logos/', null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    def __str__(self): return f"{self.sport} | {self.name}"

class Match(models.Model):
    GROUP_CHOICES = [("A", "A"), ("B", "B"), ("A&B", "A & B")]
    TYPE_CHOICES = [
        ("RR", "Round Robin"), ("SF1", "Semi Finals 1"), ("SF2", "Semi Finals 2"),
        ("P56", "5-6 Position"), ("P34", "3-4 Position"), ("F", "Finals"),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="matches")
    match_no = models.IntegerField()
    group = models.CharField(max_length=3, choices=GROUP_CHOICES)
    match_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    opponent_rule = models.CharField(max_length=200)
    team1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="home_matches")
    team2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="away_matches")
    team1_players = models.CharField(max_length=600, blank=True, null=True)
    team2_players = models.CharField(max_length=600, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    venue_type = models.CharField(max_length=20)
    venue_no = models.CharField(max_length=10)
    winner = models.CharField(max_length=100, null=True, blank=True)
    loser = models.CharField(max_length=100, null=True, blank=True)
    completed = models.BooleanField(default=False)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)
    
    def __str__(self): return f"{self.event} | {self.match_no}"
    
    def is_bracket_match(self):
        rule = (self.opponent_rule or "").lower()
        return any(x in rule for x in ["1st", "2nd", "3rd", "winner", "loser"])
    
    @property
    def player_count_hint(self):
        if "bridge" in self.event.sport.name.lower(): return "4-6"
        if "swimming" in self.event.sport.name.lower(): return "Participant"
        if "double" in self.event.name.lower(): return "2"
        return "1"

    @property
    def is_bracket_match(self):
        # Returns True if this is a semi-final, final, or position match
        return self.match_type in ['SF1', 'SF2', 'P56', 'P34', 'F']

    @property
    def bracket_ready(self):
        # Returns True if the placeholder has been filled with real teams
        return self.team1 is not None and self.team2 is not None


class ChampionshipStanding(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    gross_total = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    penalty_points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    bronze = models.IntegerField(default=0)
    def __str__(self): return f"{self.team} | {self.total_points}"

class BridgeGroupResult(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.CharField(max_length=1)
    # Team ranking fields (These are the ones the Admin is looking for)
    first = models.ForeignKey('Team', related_name='bridge_first', on_delete=models.CASCADE)
    second = models.ForeignKey('Team', related_name='bridge_second', on_delete=models.CASCADE)
    third = models.ForeignKey('Team', related_name='bridge_third', on_delete=models.CASCADE)
    
    # Raw score fields for persistence
    first_score = models.FloatField(default=0.0)
    second_score = models.FloatField(default=0.0)
    third_score = models.FloatField(default=0.0)

class SwimmingResult(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    first = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_1st")
    second = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_2nd")
    third = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_3rd")
    fourth = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_4th")
    fifth = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_5th")
    sixth = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="swim_6th")


class ManualEventResult(models.Model):
    """Independent manual entry for championship points."""
    event_id = models.IntegerField(unique=True) # 1 to 17
    event_name = models.CharField(max_length=100)
    
    # Store data as JSON to easily map Team -> (Position, Points)
    # Example: {"T1": {"pos": 1, "pts": 100}, "T2": {"pos": 2, "pts": 70}}
    results_data = models.JSONField(default=dict)

    class Meta:
        ordering = ['event_id']

    def __str__(self):
        return f"Event {self.event_id}: {self.event_name}"