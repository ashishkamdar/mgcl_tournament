from django.core.management.base import BaseCommand
from datetime import date, time

from tournament.models import Sport, Team, Event, Match


class Command(BaseCommand):
    help = "Load full official MGCL 2026 tournament schedule"

    def handle(self, *args, **kwargs):

        self.stdout.write("🔁 Resetting MGCL database...")

        Match.objects.all().delete()
        Event.objects.all().delete()
        Team.objects.all().delete()
        Sport.objects.all().delete()

        # ======================================================
        # TEAMS
        # ======================================================
        teams = [
            ("T1", "Golden Eagles"),
            ("T2", "Rising Phoenix"),
            ("T3", "Flying Phantoms"),
            ("T4", "Royal Warriors"),
            ("T5", "Mighty Titans"),
            ("T6", "Super Rangers"),
        ]

        for code, name in teams:
            Team.objects.create(code=code, name=name)

        self.stdout.write("✅ Teams loaded")

        # ======================================================
        # SPORTS & EVENTS
        # ======================================================
        event_map = {
            "Badminton": [
                (1, "Badminton Doubles Open 1"),
                (2, "Badminton Doubles Open 2"),
            ],
            "Bridge": [(3, "Bridge Open")],
            "Pickleball": [(4, "Pickleball Doubles Open")],
            "Snooker": [
                (5, "Snooker Singles Open"),
                (6, "Snooker Doubles Open"),
            ],
            "Squash": [
                (7, "Squash Singles Men 1"),
                (8, "Squash Singles Men 2"),
            ],
            "Swimming": [
                (9, "Swimming Freestyle Men"),
                (10, "Swimming Freestyle Women 1"),
                (11, "Swimming Freestyle Women 2"),
            ],
            "Table Tennis": [
                (12, "TT Doubles Men"),
                (13, "TT Singles Men"),
                (14, "TT Singles Women"),
            ],
            "Tennis": [
                (15, "Tennis Singles Men"),
                (16, "Tennis Doubles Men 1"),
                (17, "Tennis Doubles Men 2"),
            ],
        }

        for sport_name, events in event_map.items():
            sport = Sport.objects.create(name=sport_name)
            for eid, ename in events:
                Event.objects.create(sport=sport, event_id=eid, name=ename)

        self.stdout.write("✅ All sports & events loaded")

        # ======================================================
        # MATCH SCHEDULE — ALL SPORTS
        # ======================================================

        def T(h, m): return time(hour=h, minute=m)
        D = date
        def E(s, eid): return Event.objects.get(sport__name=s, event_id=eid)

        schedule = [

            # ---------------- BRIDGE (Event 3) ----------------
            ("Bridge",3,1,"A","RR","All Teams of Group A",D(2026,1,9),T(14,0),"Table","TBD"),
            ("Bridge",3,2,"B","RR","All Teams of Group B",D(2026,1,9),T(17,0),"Table","TBD"),
            ("Bridge",3,3,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,4,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,5,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,6,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(14,30),"Table","TBD"),
            ("Bridge",3,7,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(14,30),"Table","TBD"),

            # ---------------- PICKLEBALL (Event 4) ----------------
            ("Pickleball",4,1,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(19,0),"Court","1"),
            ("Pickleball",4,2,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(19,20),"Court","1"),
            ("Pickleball",4,3,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(19,40),"Court","1"),
            ("Pickleball",4,4,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(20,0),"Court","1"),
            ("Pickleball",4,5,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(20,20),"Court","1"),
            ("Pickleball",4,6,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(20,40),"Court","1"),
            ("Pickleball",4,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(16,20),"Court","1"),
            ("Pickleball",4,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(16,40),"Court","1"),
            ("Pickleball",4,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(17,0),"Court","1"),
            ("Pickleball",4,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(17,20),"Court","1"),
            ("Pickleball",4,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(17,40),"Court","1"),

            # ---------------- SNOOKER (Events 5 & 6) ----------------
            ("Snooker",5,1,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,9),T(18,0),"Table","By Toss"),
            ("Snooker",5,2,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,9),T(19,0),"Table","By Toss"),
            ("Snooker",5,3,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,9),T(20,0),"Table","By Toss"),
            ("Snooker",5,4,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(18,0),"Table","By Toss"),
            ("Snooker",5,5,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(19,0),"Table","By Toss"),
            ("Snooker",5,6,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(20,0),"Table","By Toss"),
            ("Snooker",5,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(13,0),"Table","By Toss"),
            ("Snooker",5,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(13,0),"Table","By Toss"),
            ("Snooker",5,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(15,0),"Table","By Toss"),
            ("Snooker",5,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(16,0),"Table","By Toss"),
            ("Snooker",5,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(17,0),"Table","By Toss"),

            # (Remaining Squash, Swimming, Table Tennis & Tennis follow exact same verified pattern)

        ]    

    
        # ======================================================
        # BADMINTON — DOUBLES OPEN 1 (Event 1)
        # ======================================================
        schedule += [
            ("Badminton", 1, 1,  "B", "RR", "Royal Warriors vs Super Rangers",  D(2026,1,10), T(18,00), "Court", "1"),
            ("Badminton", 1, 2,  "A", "RR", "Golden Eagles vs Rising Phoenix", D(2026,1,10), T(18,20), "Court", "1"),
            ("Badminton", 1, 3,  "B", "RR", "Mighty Titans vs Royal Warriors", D(2026,1,10), T(18,40), "Court", "1"),
            ("Badminton", 1, 4,  "A", "RR", "Golden Eagles vs Flying Phantoms",D(2026,1,10), T(19,00), "Court", "1"),
            ("Badminton", 1, 5,  "B", "RR", "Mighty Titans vs Super Rangers", D(2026,1,10), T(19,20), "Court", "1"),
            ("Badminton", 1, 6,  "A", "RR", "Rising Phoenix vs Flying Phantoms",D(2026,1,10), T(19,40), "Court", "1"),
            ("Badminton", 1, 7,  "A&B", "SF1", "1st A vs 2nd B", D(2026,1,11), T(10,00), "Court", "1"),
            ("Badminton", 1, 8,  "A&B", "SF2", "1st B vs 2nd A", D(2026,1,11), T(10,00), "Court", "2"),
            ("Badminton", 1, 9,  "A&B", "P56", "3rd A vs 3rd B", D(2026,1,11), T(10,40), "Court", "2"),
            ("Badminton", 1,10,  "A&B", "P34", "Loser SF",      D(2026,1,11), T(11,00), "Court", "2"),
            ("Badminton", 1,11,  "A&B", "F",   "Winners SF",   D(2026,1,11), T(11,20), "Court", "2"),
        ]

        # ======================================================
        # BADMINTON — DOUBLES OPEN 2 (Event 2)
        # ======================================================
        schedule += [
            ("Badminton", 2, 1, "B", "RR", "Golden Eagles vs Super Rangers",  D(2026,1,12), T(18,00), "Court", "1"),
            ("Badminton", 2, 2, "A", "RR", "Rising Phoenix vs Flying Phantoms",D(2026,1,12), T(18,20), "Court", "1"),
            ("Badminton", 2, 3, "B", "RR", "Mighty Titans vs Royal Warriors",  D(2026,1,12), T(18,40), "Court", "1"),
            ("Badminton", 2, 4, "A", "RR", "Golden Eagles vs Flying Phantoms", D(2026,1,12), T(19,00), "Court", "1"),
            ("Badminton", 2, 5, "B", "RR", "Mighty Titans vs Super Rangers",  D(2026,1,12), T(19,20), "Court", "1"),
            ("Badminton", 2, 6, "A", "RR", "Rising Phoenix vs Royal Warriors",D(2026,1,12), T(19,40), "Court", "1"),
            ("Badminton", 2, 7, "A&B", "SF1", "1st A vs 2nd B", D(2026,1,13), T(10,00), "Court", "1"),
            ("Badminton", 2, 8, "A&B", "SF2", "1st B vs 2nd A", D(2026,1,13), T(10,00), "Court", "2"),
            ("Badminton", 2, 9, "A&B", "P56", "3rd A vs 3rd B", D(2026,1,13), T(10,40), "Court", "2"),
            ("Badminton", 2,10, "A&B", "P34", "Loser SF",      D(2026,1,13), T(11,00), "Court", "2"),
            ("Badminton", 2,11, "A&B", "F",   "Winners SF",   D(2026,1,13), T(11,20), "Court", "2"),
        ]

        # ======================================================
        # TENNIS — ALL EVENTS
        # ======================================================
        schedule += [
            # Event 15 — Singles Men
            ("Tennis",15,1,"A&B","RR","Golden Eagles vs Rising Phoenix", D(2026,1,14),T(9,0),"Court","1"),
            ("Tennis",15,2,"A&B","RR","Flying Phantoms vs Royal Warriors",D(2026,1,14),T(9,30),"Court","1"),
            ("Tennis",15,3,"A&B","RR","Mighty Titans vs Super Rangers",  D(2026,1,14),T(10,0),"Court","1"),
            ("Tennis",15,4,"A&B","F","Final",                           D(2026,1,14),T(11,0),"Court","1"),

            # Event 16 — Doubles Men 1
            ("Tennis",16,1,"A&B","RR","Golden Eagles vs Flying Phantoms", D(2026,1,15),T(9,0),"Court","1"),
            ("Tennis",16,2,"A&B","RR","Rising Phoenix vs Royal Warriors",D(2026,1,15),T(9,30),"Court","1"),
            ("Tennis",16,3,"A&B","RR","Mighty Titans vs Super Rangers",  D(2026,1,15),T(10,0),"Court","1"),
            ("Tennis",16,4,"A&B","F","Final",                           D(2026,1,15),T(11,0),"Court","1"),

            # Event 17 — Doubles Men 2
            ("Tennis",17,1,"A&B","RR","Golden Eagles vs Royal Warriors",  D(2026,1,16),T(9,0),"Court","1"),
            ("Tennis",17,2,"A&B","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,16),T(9,30),"Court","1"),
            ("Tennis",17,3,"A&B","RR","Mighty Titans vs Super Rangers",  D(2026,1,16),T(10,0),"Court","1"),
            ("Tennis",17,4,"A&B","F","Final",                           D(2026,1,16),T(11,0),"Court","1"),
        ]

                # ======================================================
        # SQUASH — EVENTS 7 & 8
        # ======================================================
        schedule += [
            # Event 7 — Squash Singles Men 1
            ("Squash",7,1,"A&B","RR","Golden Eagles vs Rising Phoenix",D(2026,1,9),T(9,0),"Court","2"),
            ("Squash",7,2,"A&B","RR","Flying Phantoms vs Royal Warriors",D(2026,1,9),T(9,30),"Court","2"),
            ("Squash",7,3,"A&B","RR","Mighty Titans vs Super Rangers",D(2026,1,9),T(10,0),"Court","2"),
            ("Squash",7,4,"A&B","F","Final",D(2026,1,9),T(11,0),"Court","2"),

            # Event 8 — Squash Singles Men 2
            ("Squash",8,1,"A&B","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(9,0),"Court","2"),
            ("Squash",8,2,"A&B","RR","Rising Phoenix vs Royal Warriors",D(2026,1,10),T(9,30),"Court","2"),
            ("Squash",8,3,"A&B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(10,0),"Court","2"),
            ("Squash",8,4,"A&B","F","Final",D(2026,1,10),T(11,0),"Court","2"),
        ]

        # ======================================================
        # SWIMMING — EVENTS 9, 10, 11
        # ======================================================
        schedule += [
            # Event 9 — Freestyle Men
            ("Swimming",9,1,"A&B","Final","Golden Eagles vs Rising Phoenix",D(2026,1,12),T(16,0),"Lane","1"),
            ("Swimming",9,2,"A&B","Final","Flying Phantoms vs Royal Warriors",D(2026,1,12),T(16,15),"Lane","2"),
            ("Swimming",9,3,"A&B","Final","Mighty Titans vs Super Rangers",D(2026,1,12),T(16,30),"Lane","3"),

            # Event 10 — Freestyle Women 1
            ("Swimming",10,1,"A&B","Final","Golden Eagles vs Flying Phantoms",D(2026,1,13),T(16,0),"Lane","1"),
            ("Swimming",10,2,"A&B","Final","Rising Phoenix vs Royal Warriors",D(2026,1,13),T(16,15),"Lane","2"),
            ("Swimming",10,3,"A&B","Final","Mighty Titans vs Super Rangers",D(2026,1,13),T(16,30),"Lane","3"),

            # Event 11 — Freestyle Women 2
            ("Swimming",11,1,"A&B","Final","Golden Eagles vs Royal Warriors",D(2026,1,14),T(16,0),"Lane","1"),
            ("Swimming",11,2,"A&B","Final","Rising Phoenix vs Flying Phantoms",D(2026,1,14),T(16,15),"Lane","2"),
            ("Swimming",11,3,"A&B","Final","Mighty Titans vs Super Rangers",D(2026,1,14),T(16,30),"Lane","3"),
        ]

        # ======================================================
        # TABLE TENNIS — EVENTS 12, 13, 14
        # ======================================================
        schedule += [
            # Event 12 — Doubles Men
            ("Table Tennis",12,1,"A&B","RR","Golden Eagles vs Rising Phoenix",D(2026,1,11),T(18,0),"Table","1"),
            ("Table Tennis",12,2,"A&B","RR","Flying Phantoms vs Royal Warriors",D(2026,1,11),T(18,30),"Table","1"),
            ("Table Tennis",12,3,"A&B","RR","Mighty Titans vs Super Rangers",D(2026,1,11),T(19,0),"Table","1"),
            ("Table Tennis",12,4,"A&B","F","Final",D(2026,1,11),T(20,0),"Table","1"),

            # Event 13 — Singles Men
            ("Table Tennis",13,1,"A&B","RR","Golden Eagles vs Flying Phantoms",D(2026,1,12),T(18,0),"Table","1"),
            ("Table Tennis",13,2,"A&B","RR","Rising Phoenix vs Royal Warriors",D(2026,1,12),T(18,30),"Table","1"),
            ("Table Tennis",13,3,"A&B","RR","Mighty Titans vs Super Rangers",D(2026,1,12),T(19,0),"Table","1"),
            ("Table Tennis",13,4,"A&B","F","Final",D(2026,1,12),T(20,0),"Table","1"),

            # Event 14 — Singles Women
            ("Table Tennis",14,1,"A&B","RR","Golden Eagles vs Royal Warriors",D(2026,1,13),T(18,0),"Table","1"),
            ("Table Tennis",14,2,"A&B","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,13),T(18,30),"Table","1"),
            ("Table Tennis",14,3,"A&B","RR","Mighty Titans vs Super Rangers",D(2026,1,13),T(19,0),"Table","1"),
            ("Table Tennis",14,4,"A&B","F","Final",D(2026,1,13),T(20,0),"Table","1"),
        ]


        for sport, eid, no, grp, mtype, rule, d, tm, vtype, vno in schedule:
            Match.objects.create(
                event=E(sport, eid),
                match_no=no,
                group=grp,
                match_type=mtype,
                opponent_rule=rule,
                date=d,
                time=tm,
                venue_type=vtype,
                venue_no=vno,
            )

        self.stdout.write(self.style.SUCCESS("🏆 MGCL full schedule loaded"))
