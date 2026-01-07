from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tournament.models import Team

class Command(BaseCommand):
    help = "Generates login accounts for all teams"

    def handle(self, *args, **kwargs):
        teams = Team.objects.all()
        for t in teams:
            # Generate username: "Golden Eagles" -> "golden_eagles"
            username = t.name.lower().replace(" ", "_")
            password = f"{username}123"  # Simple default password
            
            # Create or Get User
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"✅ Created User: {username} (Pass: {password})")
            
            # Link to Team
            t.account = user
            t.save()
            self.stdout.write(f"   Linked to Team: {t.name}")

        self.stdout.write(self.style.SUCCESS("🎉 All Team Accounts Ready!"))