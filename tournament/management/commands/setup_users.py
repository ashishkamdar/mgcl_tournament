from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tournament.models import Team

class Command(BaseCommand):
    help = "Creates Admin, Referee, and Team Captain users automatically"

    def handle(self, *args, **kwargs):
        self.stdout.write("👤 Setting up System Users...")

        # 1. CREATE SUPERUSER (adminuser)
        if not User.objects.filter(username='adminuser').exists():
            User.objects.create_superuser('adminuser', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("   ✅ Superuser created: 'adminuser' / 'admin123'"))
        else:
            self.stdout.write("   ℹ️  Superuser 'adminuser' already exists.")

        # 2. CREATE REFEREE (Staff)
        ref, created = User.objects.get_or_create(username='referee')
        ref.set_password('referee123')
        ref.is_staff = True  # <--- CRITICAL: Gives access to "Enter Score" buttons
        ref.save()
        self.stdout.write(self.style.SUCCESS("   ✅ Referee created: 'referee' / 'referee123'"))

        # 3. CREATE TEAM CAPTAINS
        teams = Team.objects.all()
        if not teams.exists():
            self.stdout.write(self.style.WARNING("   ⚠️  No teams found! Run load_mgcl_full first."))
            return

        count = 0
        for team in teams:
            # Generate username: "Golden Eagles" -> "golden_eagles"
            username = team.name.lower().replace(" ", "_")
            password = f"{username}123"

            # Create or Get User
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.save()

            # Link User to Team
            team.account = user
            team.save()
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f"   ✅ Linked {count} Team Captains (e.g., 'golden_eagles' / 'golden_eagles123')"))
        self.stdout.write(self.style.SUCCESS("🎉 SYSTEM READY!"))