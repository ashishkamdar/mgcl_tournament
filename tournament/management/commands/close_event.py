from django.core.management.base import BaseCommand
from tournament.models import Event
from tournament.engine import update_championship


class Command(BaseCommand):
    help = "Finalize an event: compute rankings, assign points & medals"

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=int)
        parser.add_argument("event_type", type=str)  # SINGLE / DOUBLE / BRIDGE

    def handle(self, *args, **kwargs):
        event_id = kwargs["event_id"]
        event_type = kwargs["event_type"]

        event = Event.objects.get(id=event_id)
        update_championship(event, event_type)

        self.stdout.write(self.style.SUCCESS(f"Event {event} closed successfully"))
