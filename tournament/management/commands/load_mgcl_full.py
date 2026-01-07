import random
import re # Added for text parsing
from django.db.models import Q
from django.core.management.base import BaseCommand
from datetime import date, time
from tournament.models import Sport, Team, Event, Match, Player, ChampionshipStanding

class Command(BaseCommand):
    help = "Load full official MGCL 2026 schedule with parsed Teams and Random Rosters"

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
        # 2. TEAMS
        # ======================================================
        teams_data = [
            ("T1", "Golden Eagles", "Niyam Turakhia & Vipul Shah", "A"),
            ("T2", "Rising Phoenix", "Vijay Mulchandani & Deven Sheth", "A"),
            ("T3", "Flying Phantoms", "Sudhir Gupta & Paresh Zaveri", "A"),
            ("T4", "Royal Warriors", "Vijay Ria & Nikhil Sharma", "B"),
            ("T5", "Mighty Titans", "Rohinton Dadyburjor", "B"),
            ("T6", "Super Rangers", "Atul Shah & Nitin Kothari", "B"),
        ]

        # Map Name -> Team Object for easy lookup
        team_lookup = {}
        team_objs = {}
        
        for code, name, owners, pool in teams_data:
            t = Team.objects.create(code=code, name=name, owners=owners, pool=pool)
            team_objs[code] = t
            team_lookup[name.lower()] = t # Case-insensitive lookup
            
            ChampionshipStanding.objects.create(team=t, total_points=0, gold=0, silver=0, bronze=0)
        
        self.stdout.write("✅ Teams & Owners loaded")

        # ======================================================
        # 3. REAL PLAYER ROSTERS
        # ======================================================
        full_roster_data = [
            # --- T1 Golden Eagles ---
            ("T1", "Badminton", "Ashish Kamdar"), ("T1", "Badminton", "Bhavin Doshi"), ("T1", "Badminton", "Deepak Shah"), ("T1", "Badminton", "Pushkar Kulkarni"),
            ("T1", "Bridge", "Bankim Mehta"), ("T1", "Bridge", "Bipin Savla"), ("T1", "Bridge", "Hemant shah"), ("T1", "Bridge", "Himanshu Sanghavi"),
            ("T1", "Pickleball", "Ankit Gala"), ("T1", "Pickleball", "Dev S Thakkar"),
            ("T1", "Snooker", "Ajay Thakar"), ("T1", "Snooker", "Ashmi Chheda"), ("T1", "Snooker", "Shomeer Varadkar"),
            ("T1", "Squash", "Ashish Gavankar"), ("T1", "Squash", "Pranay Motta"),
            ("T1", "Swimming", "Jaini Gogri"), ("T1", "Swimming", "Shloka Motta"), ("T1", "Swimming", "Vedant Ajmera"), ("T1", "Swimming", "Lakshmi Raja"),
            ("T1", "TT", "Lalit Desai"), ("T1", "TT", "Mahendra Sharma"), ("T1", "TT", "Pankaj Naik"),
            ("T1", "Tennis", "Himanshu Ashar"), ("T1", "Tennis", "Hitesh Parekh"), ("T1", "Tennis", "Jayesh Shah"), ("T1", "Tennis", "Nitin Ashar"), ("T1", "Tennis", "Sandeep Parikh"),

            # --- T2 Rising Phoenix ---
            ("T2", "Badminton", "Miheer Moghe"), ("T2", "Badminton", "Rakesh Shah"), ("T2", "Badminton", "Pujan Shah"), ("T2", "Badminton", "Rajesh Mansinghani"),
            ("T2", "Bridge", "Deepak Mehta"), ("T2", "Bridge", "Raj Kailat"), ("T2", "Bridge", "Monica Advani"), ("T2", "Bridge", "Neha Mehta"),
            ("T2", "Pickleball", "Parth Goyal"), ("T2", "Pickleball", "Sanjog Lunkad"),
            ("T2", "Snooker", "Ninad Aolaskar"), ("T2", "Snooker", "Poras Shah"), ("T2", "Snooker", "Venkateswaran Subramanian"),
            ("T2", "Squash", "Chiraag Shah"), ("T2", "Squash", "Krishna Rao"),
            ("T2", "Swimming", "Riya Bawkar"), ("T2", "Swimming", "Sharvari R. Desai"), ("T2", "Swimming", "Pankaj Shah"),
            ("T2", "TT", "Sushma Shah"), ("T2", "TT", "Ajit Gandhi"), ("T2", "TT", "Janak Thakkar"), ("T2", "TT", "Percy Patel"),
            ("T2", "Tennis", "Anil Tahiliani"), ("T2", "Tennis", "Eshit Sheth"), ("T2", "Tennis", "Nanik Rupani"), ("T2", "Tennis", "Rajiv Kamdar"), ("T2", "Tennis", "Srinivasan Ganesan"),

            # --- T3 Flying Phantoms ---
            ("T3", "Badminton", "Jatin Karani"), ("T3", "Badminton", "Priyank Dedhia"), ("T3", "Badminton", "Purav Parekh"), ("T3", "Badminton", "S Rammohan Rao"),
            ("T3", "Bridge", "Pankaj Tanna"), ("T3", "Bridge", "Viresh Kamdar"), ("T3", "Bridge", "Sunil Desai"), ("T3", "Bridge", "Yogeshwar Banavali"),
            ("T3", "Pickleball", "Bhumika Shah"), ("T3", "Pickleball", "Chirag Kenia"),
            ("T3", "Snooker", "Aditya Agarwal"), ("T3", "Snooker", "Amishi Chheda"), ("T3", "Snooker", "Mehrnosh Billimoria"),
            ("T3", "Squash", "Raj Goshar"), ("T3", "Squash", "Rohan Vora"),
            ("T3", "Swimming", "Hetanshi Kamdar"), ("T3", "Swimming", "Malvika Anand lyer"), ("T3", "Swimming", "Hasmukh Haria"),
            ("T3", "TT", "Ira Naik"), ("T3", "TT", "Alok Shah"), ("T3", "TT", "Kartik Kumar raja"), ("T3", "TT", "Nagendra Prabhu"),
            ("T3", "Tennis", "Harsh Gandhi"), ("T3", "Tennis", "Nishit Mehta"), ("T3", "Tennis", "Rohan Bawkar"), ("T3", "Tennis", "Sanjiv Shah"), ("T3", "Tennis", "Sarju Jhaveri"),

            # --- T4 Royal Warriors ---
            ("T4", "Badminton", "Ashwin Mulchandani"), ("T4", "Badminton", "Hormuzd Madan"), ("T4", "Badminton", "Jenil Gogri"), ("T4", "Badminton", "Rukshad Daruvala"),
            ("T4", "Bridge", "Paras Savla"), ("T4", "Bridge", "Shruti Savla"), ("T4", "Bridge", "Ravindra Joglekar"), ("T4", "Bridge", "Sonali Sheth"),
            ("T4", "Pickleball", "Jehan Mulchandani"), ("T4", "Pickleball", "Nimesh Kampani"),
            ("T4", "Snooker", "Amit Thakkar"), ("T4", "Snooker", "Jatin N Sadarangani"), ("T4", "Snooker", "Vikram Chande"),
            ("T4", "Squash", "Abhishek Samir Bhuta"), ("T4", "Squash", "Sumer Mehta"),
            ("T4", "Swimming", "Aarthi Shetty"), ("T4", "Swimming", "Ruchi Shah"), ("T4", "Swimming", "Jai Dhanani"),
            ("T4", "TT", "Natasha Sarkar"), ("T4", "TT", "Ajit Bodas"), ("T4", "TT", "Bhavik Visaria"), ("T4", "TT", "Pranav Parekh"),
            ("T4", "Tennis", "Atul Parekh"), ("T4", "Tennis", "Christopher Lopes"), ("T4", "Tennis", "Dharmesh Hemani"), ("T4", "Tennis", "Rokshad Palkhivala"), ("T4", "Tennis", "Siddharth Chheda"),

            # --- T5 Mighty Titans ---
            ("T5", "Badminton", "Akshay Pawar"), ("T5", "Badminton", "Aman Dedhia"), ("T5", "Badminton", "Anshul Trivedi"), ("T5", "Badminton", "Kartik Mody"),
            ("T5", "Bridge", "Rajesh Shah"), ("T5", "Bridge", "Dr. Medha Ambiye"), ("T5", "Bridge", "Mahendra G Ved"), ("T5", "Bridge", "Dinyar Wadia"),
            ("T5", "Pickleball", "Pranav Rajguru"), ("T5", "Pickleball", "Shubh Gautam Pomani"),
            ("T5", "Snooker", "Deepak S Sukhija"), ("T5", "Snooker", "Devendra Joshi"), ("T5", "Snooker", "Nishit Chandan"),
            ("T5", "Squash", "Khushru Tampal"), ("T5", "Squash", "Param kiran Maru"),
            ("T5", "Swimming", "Niyati S Kenia"), ("T5", "Swimming", "Sanyogita Aolaskar"), ("T5", "Swimming", "Shashank Bawkar"),
            ("T5", "TT", "Sharmila Mauskar"), ("T5", "TT", "Paresh Ghatalia"), ("T5", "TT", "Rajesh Dave"), ("T5", "TT", "Raman lyer"),
            ("T5", "Tennis", "Aditya Barve"), ("T5", "Tennis", "Kartik B Sheth"), ("T5", "Tennis", "Prasanna Shah"), ("T5", "Tennis", "Rajesh Kishnani"), ("T5", "Tennis", "Tej Mulchandani"),

            # --- T6 Super Rangers ---
            ("T6", "Badminton", "Aakash Parikh"), ("T6", "Badminton", "Palak shah"), ("T6", "Badminton", "Prashant Gada"), ("T6", "Badminton", "Suketu sheth"),
            ("T6", "Bridge", "Priya Gupta"), ("T6", "Bridge", "Dr.Mita Doshi"), ("T6", "Bridge", "Meena Tanna"), ("T6", "Bridge", "Cyrus Dalal"),
            ("T6", "Pickleball", "Chaitanya Rao"), ("T6", "Pickleball", "Deep Karani"),
            ("T6", "Snooker", "Arun Agrawal"), ("T6", "Snooker", "Darshan Shah"), ("T6", "Snooker", "Naresh sadarangani"),
            ("T6", "Squash", "Dev Sheth"), ("T6", "Squash", "Khush Gautam Pomani"),
            ("T6", "Swimming", "Pooja Moghe"), ("T6", "Swimming", "Shikha kanakia"), ("T6", "Swimming", "Abhinav Chheda"),
            ("T6", "TT", "Gauri Parulkar"), ("T6", "TT", "Kaushik Pithadia"), ("T6", "TT", "Sharukh Karkaria"), ("T6", "TT", "Vinit Gandhi"),
            ("T6", "Tennis", "Cusrow Sadri"), ("T6", "Tennis", "Jvalant Sampat"), ("T6", "Tennis", "Mahesh Shah"), ("T6", "Tennis", "Pradip Bhat"), ("T6", "Tennis", "Umesh Ahuja"),
        ]

        player_count = 0
        for t_code, s_label, p_name in full_roster_data:
            team = team_objs.get(t_code)
            if team:
                Player.objects.get_or_create(name=p_name, team=team, sport_label=s_label)
                player_count += 1

        self.stdout.write(f"✅ {player_count} Players loaded with sport rosters")

        # ======================================================
        # 4. SPORTS & EVENTS
        # ======================================================
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

        self.stdout.write("✅ Sports & Events loaded")

        # ======================================================
        # 5. MATCH SCHEDULE
        # ======================================================
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
        for eid, ename, court in [(15,"Singles Men","1"), (16,"Doubles Men 1","2"), (17,"Doubles Men 2","3")]:
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
        schedule += [
            ("Squash",7,1,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(19,0),"Court","1"),
            ("Squash",7,2,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(19,20),"Court","1"),
            ("Squash",7,3,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(19,40),"Court","1"),
            ("Squash",7,4,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(20,0),"Court","1"),
            ("Squash",7,5,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(20,20),"Court","1"),
            ("Squash",7,6,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(20,40),"Court","1"),
            ("Squash",7,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(15,40),"Court","1"),
            ("Squash",7,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(15,40),"Court","2"),
            ("Squash",7,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(16,20),"Court","2"),
            ("Squash",7,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(16,40),"Court","2"),
            ("Squash",7,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(17,0),"Court","2"),
            ("Squash",8,1,"B","RR","Royal Warriors vs Super Rangers",D(2026,1,10),T(19,0),"Court","2"),
            ("Squash",8,2,"A","RR","Golden Eagles vs Rising Phoenix",D(2026,1,10),T(19,20),"Court","2"),
            ("Squash",8,3,"B","RR","Mighty Titans vs Royal Warriors",D(2026,1,10),T(19,40),"Court","2"),
            ("Squash",8,4,"A","RR","Golden Eagles vs Flying Phantoms",D(2026,1,10),T(20,0),"Court","2"),
            ("Squash",8,5,"B","RR","Mighty Titans vs Super Rangers",D(2026,1,10),T(20,20),"Court","2"),
            ("Squash",8,6,"A","RR","Rising Phoenix vs Flying Phantoms",D(2026,1,10),T(20,40),"Court","2"),
            ("Squash",8,7,"A&B","SF1","1st of Group A vs 2nd of Group B",D(2026,1,11),T(16,0),"Court","1"),
            ("Squash",8,8,"A&B","SF2","1st of Group B vs 2nd of Group A",D(2026,1,11),T(16,0),"Court","2"),
            ("Squash",8,9,"A&B","P56","3rd of Group A vs 3rd of Group B",D(2026,1,11),T(16,20),"Court","1"),
            ("Squash",8,10,"A&B","P34","Loser of Semi Finals",D(2026,1,11),T(16,40),"Court","1"),
            ("Squash",8,11,"A&B","F","Winners of Semi Finals",D(2026,1,11),T(17,0),"Court","1"),
        ]
        # SWIMMING
        schedule += [
            ("Swimming",9,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,0),"Lane","1"),
            ("Swimming",10,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,5),"Lane","1"),
            ("Swimming",11,1,"A&B","F","All Teams (Finals)",D(2026,1,11),T(18,10),"Lane","1"),
        ]
        # TABLE TENNIS
        for eid, ename, t_table in [(12, "TT Doubles", "1"), (13, "TT Singles Men", "1"), (14, "TT Singles Women", "2")]:
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

        # 6. CREATE MATCHES
        match_objs = []
        for sport, eid, no, grp, mtype, rule, d, tm, vtype, vno in schedule:
            
            # --- PARSE OPPONENTS FROM RULE ---
            # e.g., "Golden Eagles Vs Flying Phantoms"
            t1_obj = None
            t2_obj = None
            
            # Try to split by case-insensitive 'vs'
            # Note: The PDF data uses "Vs", "vs", and sometimes newlines.
            # We'll normalize spaces and check.
            clean_rule = rule.replace("\n", " ").strip()
            
            # We only parse if it looks like a Versus string
            if " vs " in clean_rule.lower():
                parts = re.split(r'\s+[vV][sS]\s+', clean_rule)
                if len(parts) >= 2:
                    name1 = parts[0].strip().lower()
                    name2 = parts[1].strip().lower()
                    
                    t1_obj = team_lookup.get(name1)
                    t2_obj = team_lookup.get(name2)

            m = Match.objects.create(
                event=E(sport, eid),
                match_no=no,
                group=grp,
                match_type=mtype,
                opponent_rule=rule,
                team1=t1_obj,  # <--- LINKED HERE
                team2=t2_obj,  # <--- LINKED HERE
                date=d,
                time=tm,
                venue_type=vtype,
                venue_no=vno,
            )
            match_objs.append(m)

        self.stdout.write(f"✅ {len(match_objs)} Matches Created.")

        # ======================================================
        # 7. AUTO-ASSIGN PLAYERS (Random Placeholder)
        # ======================================================
        self.stdout.write("🎲 Randomly assigning players to matches...")
        
        for m in match_objs:
            # Skip if match has no teams yet (semi-finals, placeholders)
            if not m.team1 or not m.team2:
                continue
            
            # Determine required players based on sport
            sport_name = m.event.sport.name.lower()
            event_name = m.event.name.lower()
            
            # Logic: Doubles/Bridge = 2 players, Singles/Swimming = 1 player
            if "double" in event_name or "bridge" in sport_name:
                req_players = 2
            else:
                req_players = 1
                
            # Helper to pick players
            def pick_squad(team, s_name):
                # Filter players by team AND sport (fuzzy match for 'TT' / 'Swimming')
                candidates = Player.objects.filter(team=team)
                
                # Handling special cases for labels like "Swimming / TT" or "Table Tennis"
                if "table" in s_name or "tt" in s_name:
                    candidates = candidates.filter(Q(sport_label__icontains="Table") | Q(sport_label__icontains="TT"))
                elif "swimming" in s_name:
                    candidates = candidates.filter(sport_label__icontains="Swimming")
                else:
                    candidates = candidates.filter(sport_label__icontains=s_name)
                
                pool_list = list(candidates)
                if len(pool_list) >= req_players:
                    chosen = random.sample(pool_list, req_players)
                    return ", ".join([p.name for p in chosen])
                elif pool_list:
                    return ", ".join([p.name for p in pool_list]) # Take all if fewer than needed
                return ""

            # Assign
            m.team1_players = pick_squad(m.team1, sport_name)
            m.team2_players = pick_squad(m.team2, sport_name)
            m.save()

        self.stdout.write(self.style.SUCCESS("🏆 MGCL Setup Complete with Randomized Rosters!"))