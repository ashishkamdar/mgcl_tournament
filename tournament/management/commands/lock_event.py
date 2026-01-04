from django.core.management.base import BaseCommand
from tournament.models import Event


class Command(BaseCommand):
    help = "Lock an event to prevent further edits"

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=int)

    def handle(self, *args, **kwargs):
        event = Event.objects.get(id=kwargs["event_id"])
        event.is_locked = True
        event.save()
        self.stdout.write(self.style.SUCCESS(f"{event} locked"))
