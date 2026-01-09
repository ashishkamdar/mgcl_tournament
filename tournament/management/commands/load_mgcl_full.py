import random
import re
from django.db.models import Q
from django.db.models.signals import post_save
from django.core.management.base import BaseCommand
from datetime import date, time
from tournament.models import Sport, Team, Event, Match, Player, ChampionshipStanding

class Command(BaseCommand):
    help = "Load MGCL 2026 schedule with verified player pairs from Organiser CSV"

    def handle(self, *args, **kwargs):
        self.stdout.write("🔁 Resetting MGCL database...")

        # 1. CLEANUP
        Match.objects.all().delete()
        Event.objects.all().delete()
        Player.objects.all().delete()
        ChampionshipStanding.objects.all().delete()
        Team.objects.all().delete()
        Sport.objects.all().delete()

        # ======================================================
        # 2. TEAMS (Verified)
        # ======================================================
        teams_data = [
            ("T1", "Golden Eagles", "Niyam Turakhia & Vipul Shah", "A"),
            ("T2", "Rising Phoenix", "Vijay Mulchandani & Deven Sheth", "A"),
            ("T3", "Flying Phantoms", "Sudhir Gupta & Paresh Zaveri", "A"),
            ("T4", "Royal Warriors", "Vijay Ria & Nikhil Sharma", "B"),
            ("T5", "Mighty Titans", "Rohinton Dadyburjor", "B"),
            ("T6", "Super Rangers", "Atul Shah & Nitin Kothari", "B"),
        ]

        team_lookup = {}
        team_objs = {}
        
        for code, name, owners, pool in teams_data:
            t = Team.objects.create(code=code, name=name, owners=owners, pool=pool)
            team_objs[code] = t
            team_lookup[name.lower()] = t 
            ChampionshipStanding.objects.create(team=t, total_points=0, gold=0, silver=0, bronze=0)

        # ======================================================
        # 3. MANUALLY VERIFIED PLAYER PAIRS (Match-by-Match from CSV)
        # ======================================================
        official_pairs = {
            "T1": {
                "Badminton": ["Ashish Kamdar & Pushkar Kulkarni", "Bhavin Doshi & Deepak Shah"],
                "Bridge": ["Bankim Mehta & Bipin Savla & Hemant shah & Himanshu Sanghavi"],
                "Pickleball": ["Ankit Gala & Dev S Thakkar"],
                "Snooker": ["Ashmi Chheda", "Ajay Thakar & Shomeer Varadkar"],
                "Squash": ["Ashish Gavankar", "Pranay Motta"],
                "Swimming": ["Vedant Ajmera", "Shloka Motta", "Jaini Gogri"],
                "TT": ["Pankaj Naik & Mahendra Sharma", "Lalit Desai", "Lakshmi Raja"],
                "Tennis": ["Sandeep Parikh", "Himanshu Ashar & Jayesh Shah", "Hitesh Parekh & Nitin Ashar"]
            },
            "T2": {
                "Badminton": ["Miheer Moghe & Pujan Shah", "Rakesh Shah & Rajesh Mansinghani"],
                "Bridge": ["Monica Advani & Neha Mehta & Deepak Mehta & Raj Kailat"],
                "Pickleball": ["Parth Goyal & Sanjog Lunkad"],
                "Snooker": ["Poras Shah", "Percy Patel & Ninad Aolaskar"],
                "Squash": ["Chiraag Shah", "Krishna Rao"],
                "Swimming": ["Pankaj Shah", "Sharvari R. Desai", "Riya Bawkar"],
                "TT": ["Ajit Gandhi & Percy Patel", "Janak Thakkar", "Sushma Shah"],
                "Tennis": ["Eshit Sheth", "Rajiv Kamdar & Srinivasan Ganesan", "Anil Tahiliani & Nanik Rupani"]
            },
            "T3": {
                "Badminton": ["Priyank Dedhia & S Rammohan Rao", "Yashad Moghe & Purav Parekh"],
                "Bridge": ["Pankaj Tanna & Viresh Kamdar & Sunil Desai & Yogeshwar Banavali"],
                "Pickleball": ["Bhumika Shah & Chirag Kenia"],
                "Snooker": ["Aditya Agarwal", "Amishi Chheda & Mehrnosh Billimoria"],
                "Squash": ["Raj Goshar", "Rohan Vora"],
                "Swimming": ["Hridaan Nisar", "Hetanshi Kamdar", "Malvika Anand Iyer"],
                "TT": ["Kartik Kumar raja & Nagendra Prabhu", "Alok Shah", "Ira Naik"],
                "Tennis": ["Harsh Gandhi", "Rohan Bawkar & Sarju Jhaveri", "Nishit Mehta & Sanjiv Shah"]
            },
            "T4": {
                "Badminton": ["Hormuzd Madan & Rukshad Daruvala", "Jenil Gogri & Ashwin Mulchandani"],
                "Bridge": ["Paras Savla & Shruti Savla & Ravindra Joglekar & Sonali Sheth"],
                "Pickleball": ["Jehan Mulchandani & Nimesh Kampani"],
                "Snooker": ["Amit Thakkar", "Jatin N Sadarangani & Vikram Chande"],
                "Squash": ["Sumer Mehta", "Abhishek Samir Bhuta"],
                "Swimming": ["Jai Dhanani", "Aarthi Shetty", "Ruchi Shah"],
                "TT": ["Pranav Parekh & Ajit Bodas", "Bhavik Visaria", "Natasha Sarkar"],
                "Tennis": ["Siddharth Chheda", "Dharmesh Hemani & Rokshad Palkhivala", "Atul Parekh & Christopher Lopes"]
            },
            "T5": {
                "Badminton": ["Kartik Mody & Akshay Pawar", "Rajat Bhalla & Anshul Trivedi"],
                "Bridge": ["Mahendra G Ved & Dinyar Wadia & Shilpi Savla & Dr. Medha Ambiye"],
                "Pickleball": ["Pranav Rajguru & Shubh Gautam Pomani"],
                "Snooker": ["Devendra Joshi", "Deepak S Sukhija & Nishit Chandan"],
                "Squash": ["Khushru Tampal", "Param kiran Maru"],
                "Swimming": ["Shashank Bawkar", "Niyati S Kenia", "Sanyogita Aolaskar"],
                "TT": ["Paresh Ghatalia & Rajesh Dave", "Raman Iyer", "Sharmila Mauskar"],
                "Tennis": ["Tej Mulchandani", "Aditya Barve & Prasanna Shah", "Kartik B Sheth & Rajesh Kishnani"]
            },
            "T6": {
                "Badminton": ["Prashant Gada & Suketu sheth", "Aakash Parikh & Palak shah"],
                "Bridge": ["Priya Gupta & Dr.Mita Doshi & Meena Tanna & Cyrus Dalal"],
                "Pickleball": ["Chaitanya Rao & Deep Karani"],
                "Snooker": ["Arun Agrawal", "Darshan Shah & Naresh sadarangani"],
                "Squash": ["Khush Gautam Pomani", "Dev Sheth"],
                "Swimming": ["Chaitanya Rao", "Pooja Moghe", "Shikha kanakia"],
                "TT": ["Sharukh Karkaria & Vinit Gandhi", "Kaushik Pithadia", "Gauri Parulkar"],
                "Tennis": ["Jvalant Sampat", "Pradip Bhat & Cusrow Sadri", "Mahesh Shah & Umesh Ahuja"]
            }
        }

        # 4. SPORTS & EVENTS
        event_map = {
            "Badminton": [(1, "Badminton Doubles Open 1"), (2, "Badminton Doubles Open 2")],
            "Bridge": [(3, "Bridge Open")],
            "Pickleball": [(4, "Pickleball Doubles Open")],
            "Snooker": [(5, "Snooker Singles Open"), (6, "Snooker Doubles Open")],
            "Squash": [(7, "Squash Singles Men 1"), (8, "Squash Singles Men 2")],
            "Swimming": [(9, "Swimming Freestyle Men"), (10, "Swimming Freestyle Women 1"), (11, "Swimming Freestyle Women 2")],
            "Table Tennis": [(12, "TT Doubles Men"), (13, "TT Singles Men"), (14, "TT Singles Women")],
            "Tennis": [(15, "Tennis Singles Men"), (16, "Tennis Doubles Men 1"), (17, "Tennis Doubles Men 2")],
        }

        for sport_name, events in event_map.items():
            sport = Sport.objects.create(name=sport_name)
            for eid, ename in events:
                Event.objects.create(sport=sport, event_id=eid, name=ename)

        # 5. FULL MATCH SCHEDULE
        def T(h, m): return time(hour=h, minute=m)
        D = date
        def E(s, eid): return Event.objects.get(sport__name=s, event_id=eid)

        schedule = []
        # BRIDGE
        schedule += [
            ("Bridge",3,1,"A","RR","All Teams of Group A",D(2026,1,9),T(14,0),"Table","TBD"),
            ("Bridge",3,2,"B","RR","All Teams of Group B",D(2026,1,9),T(17,0),"Table","TBD"),
            ("Bridge",3,3,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,4,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,5,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(11,0),"Table","TBD"),
            ("Bridge",3,6,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(14,30),"Table","TBD"),
            ("Bridge",3,7,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(14,30),"Table","TBD"),
        ]
        # PICKLEBALL
        schedule += [
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
        ]
        # SNOOKER
        schedule += [
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
            ("Snooker",6,1,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,9),T(18,0),"Table","By Toss"),
            ("Snooker",6,2,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,9),T(19,0),"Table","By Toss"),
            ("Snooker",6,3,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,9),T(20,0),"Table","By Toss"),
            ("Snooker",6,4,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,13),T(18,0),"Table","By Toss"),
            ("Snooker",6,5,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,13),T(19,0),"Table","By Toss"),
            ("Snooker",6,6,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,13),T(20,0),"Table","By Toss"),
            ("Snooker",6,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,14),T(13,0),"Table","By Toss"),
            ("Snooker",6,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,14),T(13,0),"Table","By Toss"),
            ("Snooker",6,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,14),T(15,0),"Table","By Toss"),
            ("Snooker",6,10,"A&B","P34","Loser of Semi Finals",D(2026,1,14),T(16,0),"Table","By Toss"),
            ("Snooker",6,11,"A&B","F","Winners of Semi Finals",D(2026,1,14),T(17,0),"Table","By Toss"),
        ]
        # BADMINTON
        schedule += [
            ("Badminton", 1, 1,  "B", "RR", "Royal Warriors vs Super Rangers",  D(2026,1,10), T(18,0), "Court", "1"),
            ("Badminton", 1, 2,  "A", "RR", "Golden Eagles vs Rising Phoenix", D(2026,1,10), T(18,20), "Court", "1"),
            ("Badminton", 1, 3,  "B", "RR", "Mighty Titans vs Royal Warriors", D(2026,1,10), T(18,40), "Court", "1"),
            ("Badminton", 1, 4,  "A", "RR", "Golden Eagles vs Flying Phantoms",D(2026,1,10), T(19,0), "Court", "1"),
            ("Badminton", 1, 5,  "B", "RR", "Mighty Titans vs Super Rangers", D(2026,1,10), T(19,20), "Court", "1"),
            ("Badminton", 1, 6,  "A", "RR", "Rising Phoenix vs Flying Phantoms",D(2026,1,10), T(19,40), "Court", "1"),
            ("Badminton", 1, 7,  "A&B", "SF1", "1st A vs 2nd B", D(2026,1,11), T(10,0), "Court", "1"),
            ("Badminton", 1, 8,  "A&B", "SF2", "1st B vs 2nd A", D(2026,1,11), T(10,0), "Court", "2"),
            ("Badminton", 1, 9,  "A&B", "P56", "3rd A vs 3rd B", D(2026,1,11), T(10,40), "Court", "2"),
            ("Badminton", 1,10,  "A&B", "P34", "Loser SF",      D(2026,1,11), T(11,0), "Court", "2"),
            ("Badminton", 1,11,  "A&B", "F",   "Winners SF",   D(2026,1,11), T(11,20), "Court", "2"),
            ("Badminton", 2, 1, "B", "RR", "Golden Eagles vs Super Rangers",  D(2026,1,12), T(18,0), "Court", "2"),
            ("Badminton", 2, 2, "A", "RR", "Rising Phoenix vs Flying Phantoms",D(2026,1,12), T(18,20), "Court", "2"),
            ("Badminton", 2, 3, "B", "RR", "Mighty Titans vs Royal Warriors",  D(2026,1,12), T(18,40), "Court", "2"),
            ("Badminton", 2, 4, "A", "RR", "Golden Eagles vs Flying Phantoms", D(2026,1,12), T(19,0), "Court", "2"),
            ("Badminton", 2, 5, "B", "RR", "Mighty Titans vs Super Rangers",  D(2026,1,12), T(19,20), "Court", "2"),
            ("Badminton", 2, 6, "A", "RR", "Rising Phoenix vs Royal Warriors",D(2026,1,12), T(19,40), "Court", "2"),
            ("Badminton", 2, 7, "A&B", "SF1", "1st A vs 2nd B", D(2026,1,13), T(10,0), "Court", "1"),
            ("Badminton", 2, 8, "A&B", "SF2", "1st B vs 2nd A", D(2026,1,13), T(10,0), "Court", "2"),
            ("Badminton", 2, 9, "A&B", "P56", "3rd A vs 3rd B", D(2026,1,13), T(10,40), "Court", "2"),
            ("Badminton", 2,10, "A&B", "P34", "Loser SF",      D(2026,1,13), T(11,0), "Court", "2"),
            ("Badminton", 2,11, "A&B", "F",   "Winners SF",   D(2026,1,13), T(11,20), "Court", "2"),
        ]
        # TENNIS
        for eid, court in [(15,"1"), (16,"2"), (17,"3")]:
            schedule += [
                ("Tennis",eid,1,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(18,0), "Court", court),
                ("Tennis",eid,2,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(18,25), "Court", court),
                ("Tennis",eid,3,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(18,50), "Court", court),
                ("Tennis",eid,4,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(19,15), "Court", court),
                ("Tennis",eid,5,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(19,40), "Court", court),
                ("Tennis",eid,6,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(20,5),  "Court", court),
                ("Tennis",eid,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(16,0), "Court", "1"),
                ("Tennis",eid,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(16,0), "Court", "2"),
                ("Tennis",eid,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(17,15),"Court", "3"),
                ("Tennis",eid,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(17,40),"Court", "3"),
                ("Tennis",eid,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(18,5), "Court", "3"),
            ]
        # SQUASH
        for eid, court in [(7,"1"), (8,"2")]:
            schedule += [
                ("Squash",eid,1,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(19,0),"Court", court),
                ("Squash",eid,2,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(19,20),"Court", court),
                ("Squash",eid,3,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(19,40),"Court", court),
                ("Squash",eid,4,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(20,0),"Court", court),
                ("Squash",eid,5,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(20,20),"Court", court),
                ("Squash",eid,6,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(20,40),"Court", court),
                ("Squash",eid,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(15,40),"Court", court),
                ("Squash",eid,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(15,40),"Court", court),
                ("Squash",eid,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(16,20),"Court", court),
                ("Squash",eid,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(16,40),"Court", court),
                ("Squash",eid,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(17,0),"Court", court),
            ]
        # SWIMMING
        schedule += [
            ("Swimming",9,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,0),"Lane","1"),
            ("Swimming",10,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,5),"Lane","1"),
            ("Swimming",11,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,10),"Lane","1"),
        ]
        # TABLE TENNIS
        for eid, t_table in [(12, "1"), (13, "1"), (14, "2")]:
            schedule += [
                ("Table Tennis",eid,1,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(17,0), "Table", t_table),
                ("Table Tennis",eid,2,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(17,20),"Table", t_table),
                ("Table Tennis",eid,3,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(17,40),"Table", t_table),
                ("Table Tennis",eid,4,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(18,0), "Table", t_table),
                ("Table Tennis",eid,5,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(18,20),"Table", t_table),
                ("Table Tennis",eid,6,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(18,40),"Table", t_table),
                ("Table Tennis",eid,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(10,0),"Table", "1"),
                ("Table Tennis",eid,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(10,0),"Table", "2"),
                ("Table Tennis",eid,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(10,20),"Table", "2"),
                ("Table Tennis",eid,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(10,40),"Table", "2"),
                ("Table Tennis",eid,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(11,0),"Table", "2"),
            ]

        # 6. CREATE MATCHES & ASSIGN VERIFIED PLAYERS
        # Index Mapping for Events based on CSV rows
        idx_map = {
            1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0, 8: 1,
            9: 0, 10: 1, 11: 2, 12: 0, 13: 1, 14: 2, 15: 0, 16: 1, 17: 2
        }

        for sport_name, eid, no, grp, mtype, rule, d, tm, vtype, vno in schedule:
            t1_obj, t2_obj = None, None
            clean_rule = rule.replace("\n", " ").strip()
            if " vs " in clean_rule.lower():
                parts = re.split(r'\s+[vV][sS]\s+', clean_rule)
                if len(parts) >= 2:
                    t1_obj = team_lookup.get(parts[0].strip().lower())
                    t2_obj = team_lookup.get(parts[1].strip().lower())

            m = Match.objects.create(
                event=E(sport_name, eid), match_no=no, group=grp, match_type=mtype,
                opponent_rule=rule, team1=t1_obj, team2=t2_obj,
                date=d, time=tm, venue_type=vtype, venue_no=vno,
            )

            # ASSIGN OFFICIAL PAIRS
            def get_players(team, s_name, event_id):
                if not team or team.code not in official_pairs: return ""
                key_s = "TT" if "table" in s_name.lower() else s_name
                pairs_list = official_pairs[team.code].get(key_s, [])
                if not pairs_list: return ""
                idx = idx_map.get(event_id, 0)
                return pairs_list[min(idx, len(pairs_list) - 1)]

            if t1_obj: m.team1_players = get_players(t1_obj, sport_name, eid)
            if t2_obj: m.team2_players = get_players(t2_obj, sport_name, eid)
            m.save()

        # 7. TRIGGER ENGINE
        for m in Match.objects.all():
            post_save.send(sender=Match, instance=m, created=False)

        self.stdout.write(self.style.SUCCESS("🏆 MGCL Setup Complete with Corrected Pairs!"))