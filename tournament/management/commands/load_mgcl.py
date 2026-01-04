from django.core.management.base import BaseCommand
from tournament.models import Event, Group, Team, Standing


class Command(BaseCommand):
    help = "Load MGCL tournament initial data"

    def handle(self, *args, **kwargs):
        # Clean previous data
        Standing.objects.all().delete()
        Team.objects.all().delete()
        Group.objects.all().delete()
        Event.objects.all().delete()

        event = Event.objects.create(name="MGCL 2026", start_date="2026-01-01")

        # Create one hidden group
        group = Group.objects.create(event=event, name="A")

        teams_data = [
            ("T1", "Golden Eagles"),
            ("T2", "Rising Phoenix"),
            ("T3", "Flying Phantoms"),
            ("T4", "Royal Warriors"),
            ("T5", "Mighty Titans"),
            ("T6", "Super Rangers"),
        ]

        for code, name in teams_data:
            Team.objects.create(name=f"{code} - {name}", group=group)

        self.stdout.write(self.style.SUCCESS("MGCL tournament data loaded successfully"))
