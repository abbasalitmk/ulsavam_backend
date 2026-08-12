from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from districts.models import District
from users.models import User
from events.models import Event, EventConfirmation, Attendance


class Command(BaseCommand):
    help = "Seed the database with comprehensive Kerala festival and event data"

    def handle(self, *args, **options):
        self.stdout.write("Starting comprehensive data seeding...")

        # Create Districts (including Pathanamthitta)
        districts_data = [
            "Thiruvananthapuram", "Kollam", "Alappuzha", "Kottayam",
            "Idukki", "Ernakulam", "Thrissur", "Palakkad",
            "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod",
            "Pathanamthitta"
        ]

        districts = {}
        for district_name in districts_data:
            district, created = District.objects.get_or_create(name=district_name)
            districts[district_name] = district
            if created:
                self.stdout.write(f"✓ Created district: {district_name}")

        # Create Admin User
        admin_user, created = User.objects.get_or_create(
            email="admin@ulsavam.com",
            defaults={
                "display_name": "Ulsavam Admin",
                "is_staff": True,
                "is_superuser": True,
                "district": districts["Ernakulam"],
                "preferred_language": "ml"
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write("✓ Created admin user")

        # Create Event Organizers
        organizers_data = [
            ("thrissur.festival@example.com", "Thrissur Festival Committee", "Thrissur"),
            ("kochi.events@example.com", "Kochi Events Organization", "Ernakulam"),
            ("trivandrum.arts@example.com", "Trivandrum Arts Foundation", "Thiruvananthapuram"),
            ("alappuzha.culture@example.com", "Alappuzha Cultural Society", "Alappuzha"),
            ("kozhikode.literature@example.com", "Kozhikode Literature Council", "Kozhikode"),
            ("kollam.traditions@example.com", "Kollam Heritage Traditions", "Kollam"),
            ("kannur.festival@example.com", "Kannur Festival Authority", "Kannur"),
            ("palakkad.events@example.com", "Palakkad Events Management", "Palakkad"),
        ]

        organizers = {}
        for email, name, district_name in organizers_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "display_name": name,
                    "district": districts.get(district_name, districts["Ernakulam"]),
                    "is_staff": True,
                    "preferred_language": "en"
                }
            )
            organizers[email] = user
            if created:
                self.stdout.write(f"✓ Created organizer: {name}")

        # Create Sample Users
        sample_users_data = [
            ("user1@example.com", "Raj Kumar", "Thiruvananthapuram"),
            ("user2@example.com", "Priya Sharma", "Ernakulam"),
            ("user3@example.com", "Amit Patel", "Kozhikode"),
            ("user4@example.com", "Anjali Nair", "Thrissur"),
            ("user5@example.com", "Deepak Menon", "Malappuram"),
            ("user6@example.com", "Sneha Krishnan", "Alappuzha"),
            ("user7@example.com", "Arjun Singh", "Kannur"),
            ("user8@example.com", "Meera Iyer", "Kottayam"),
            ("user9@example.com", "Vikram Das", "Palakkad"),
            ("user10@example.com", "Anjana Nambiar", "Kozhikode"),
        ]

        users = {}
        for email, name, district_name in sample_users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "display_name": name,
                    "district": districts.get(district_name, districts["Ernakulam"]),
                    "preferred_language": "en"
                }
            )
            users[email] = user
            if created:
                self.stdout.write(f"✓ Created user: {name}")

        # Comprehensive Kerala Festivals & Events Data
        events_data = [
            # January
            {
                "title": "Sabarimala Makaravilakku",
                "description": "Sacred pilgrimage marking the appearance of Makara Jyothi, the celestial light at Sabarimala. One of the world's largest gatherings.",
                "category": "temple",
                "district": "Pathanamthitta",
                "venue_name": "Sabarimala Sree Dharma Sastha Temple",
                "address": "Periyar Tiger Reserve, Pathanamthitta, Kerala 689653",
                "latitude": 9.4343,
                "longitude": 77.0804,
                "event_date": datetime(2026, 1, 14).date(),
                "start_time": time(18, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Sabarimala_temple_view.jpg"
            },
            {
                "title": "Nishagandhi Dance & Music Festival",
                "description": "Premier performing arts festival featuring classical Indian dance and Hindustani/Carnatic music performances under starry skies.",
                "category": "arts_culture",
                "district": "Thiruvananthapuram",
                "venue_name": "Nishagandhi Open Air Theatre",
                "address": "Kanakakkunnu Palace Complex, Thiruvananthapuram, Kerala 695023",
                "latitude": 8.5135,
                "longitude": 76.9567,
                "event_date": datetime(2026, 1, 15).date(),
                "start_time": time(18, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Kanakakkunnu_Palace_Gate_Trivandrum.jpg"
            },
            {
                "title": "Arthunkal St. Sebastian Feast",
                "description": "Historic church feast featuring processions, traditional rituals, and the unique Ezhunallathu (crawling) pilgrimage ritual.",
                "category": "church",
                "district": "Alappuzha",
                "venue_name": "St. Andrew's Basilica",
                "address": "Arthunkal, Alappuzha, Kerala 688538",
                "latitude": 9.6853,
                "longitude": 76.2994,
                "event_date": datetime(2026, 1, 20).date(),
                "start_time": time(16, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Arthunkal_Church.jpg/1280px-Arthunkal_Church.jpg"
            },
            {
                "title": "Kerala Literature Festival (KLF) - Jan 2026",
                "description": "India's largest literary festival on Kozhikode Beach with 5 stages, author talks, book launches, and cultural performances.",
                "category": "arts_culture",
                "district": "Kozhikode",
                "venue_name": "Kozhikode Beach",
                "address": "Kozhikode Beach, Kozhikode, Kerala 673001",
                "latitude": 11.2588,
                "longitude": 75.7704,
                "event_date": datetime(2026, 1, 22).date(),
                "start_time": time(9, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Kozhikode_Beach_1.jpg/1280px-Kozhikode_Beach_1.jpg"
            },
            # February
            {
                "title": "Maramon Convention",
                "description": "Asia's largest Christian congregation on Pamba River sandbeds with gospel music, choir performances, and spiritual talks.",
                "category": "community",
                "district": "Pathanamthitta",
                "venue_name": "Pamba River Bed Sandbanks",
                "address": "Maramon (Kozhencherry), Pathanamthitta, Kerala 689642",
                "latitude": 9.3382,
                "longitude": 76.6851,
                "event_date": datetime(2026, 2, 8).date(),
                "start_time": time(9, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/39/Maramon_Convention.jpg"
            },
            {
                "title": "Machad Mamangam",
                "description": "Ancient temple festival with wooden horse motif processions and traditional folk rituals celebrating warrior heritage.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Machad Thiruvanikavu Temple",
                "address": "Wadakkanchery, Thrissur, Kerala 680582",
                "latitude": 10.6412,
                "longitude": 76.2588,
                "event_date": datetime(2026, 2, 17).date(),
                "start_time": time(16, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Thrissur_Pooram_1.jpg"
            },
            {
                "title": "Pariyanampetta Pooram",
                "description": "Temple festival featuring 21 caparisoned elephants, traditional Tholpavakoothu shadow puppetry, and ceremonial processions.",
                "category": "temple",
                "district": "Palakkad",
                "venue_name": "Pariyanampetta Bhagavathy Temple",
                "address": "Kattukulam, Palakkad, Kerala 678005",
                "latitude": 10.8924,
                "longitude": 76.4381,
                "event_date": datetime(2026, 2, 19).date(),
                "start_time": time(16, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Uthralikavu_Pooram.jpg"
            },
            {
                "title": "Chettikulangara Bharani",
                "description": "Grand temple festival with spectacular giant chariots (Kettukazhcha), traditional Kuthiyottam ritual dance, and cultural pageantry.",
                "category": "temple",
                "district": "Alappuzha",
                "venue_name": "Chettikulangara Devi Temple",
                "address": "Mavelikkara, Alappuzha, Kerala 690534",
                "latitude": 9.2558,
                "longitude": 76.5361,
                "event_date": datetime(2026, 2, 23).date(),
                "start_time": time(16, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Chettikulangara_Bharani_Kettukazhcha.jpg"
            },
            {
                "title": "Uthralikkavu Pooram",
                "description": "Temple festival with daytime elephant processions, Pandi Melam percussion orchestras, and night-time grand fireworks spectacle.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Sree Ruthira Mahakali Kavu Temple",
                "address": "Wadakkanchery, Thrissur, Kerala 680582",
                "latitude": 10.6657,
                "longitude": 76.2412,
                "event_date": datetime(2026, 2, 24).date(),
                "start_time": time(11, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Uthralikavu_Pooram.jpg"
            },
            {
                "title": "Guruvayur Aanayottam (Elephant Race)",
                "description": "Thrilling annual elephant race at sacred Krishna temple where majestic elephants race into the eastern gopuram sanctum.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Guruvayur Sree Krishna Temple",
                "address": "Guruvayur, Thrissur, Kerala 680103",
                "latitude": 10.5946,
                "longitude": 76.0411,
                "event_date": datetime(2026, 2, 28).date(),
                "start_time": time(15, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Vishukkani_setup.jpg"
            },
            # March
            {
                "title": "Chinakkathoor Pooram",
                "description": "Spectacular temple festival with 27 caparisoned elephants, massive wooden horse and bull effigies, and Panchavadyam percussion.",
                "category": "temple",
                "district": "Palakkad",
                "venue_name": "Chinakkathoor Bhagavathy Temple",
                "address": "Palappuram (Ottapalam), Palakkad, Kerala 679506",
                "latitude": 10.7712,
                "longitude": 76.3685,
                "event_date": datetime(2026, 3, 2).date(),
                "start_time": time(16, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Kalpathi_Ratholsavam.jpg"
            },
            {
                "title": "Attukal Pongala",
                "description": "World's largest gathering of women creating 10 km of sacred ritual rice pudding in a historic ceremony of devotion and sisterhood.",
                "category": "temple",
                "district": "Thiruvananthapuram",
                "venue_name": "Attukal Bhagavathy Temple",
                "address": "Attukal, Thiruvananthapuram, Kerala 695001",
                "latitude": 8.4735,
                "longitude": 76.9537,
                "event_date": datetime(2026, 3, 3).date(),
                "start_time": time(10, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Attukal_Pongala.jpg"
            },
            {
                "title": "Kodungalloor Bharani",
                "description": "Ancient ritual where the royal family leads the Aswathi Kaavutheendhal ceremony with traditional songs and temple customs.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Sree Kurumba Bhagavathy Temple",
                "address": "Kodungalloor, Thrissur, Kerala 680668",
                "latitude": 10.2223,
                "longitude": 76.2023,
                "event_date": datetime(2026, 3, 22).date(),
                "start_time": time(16, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Arattupuzha_Pooram.jpg"
            },
            {
                "title": "Kottankulangara Chamayavilakku",
                "description": "Unique festival where cross-dressed male devotees hold five-wick oil lamps in overnight procession, celebrating gender-fluid traditions.",
                "category": "temple",
                "district": "Kollam",
                "venue_name": "Kottankulangara Devi Temple",
                "address": "Chavara, Kollam, Kerala 691583",
                "latitude": 8.9868,
                "longitude": 76.5413,
                "event_date": datetime(2026, 3, 24).date(),
                "start_time": time(19, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/2/22/Chamayavilakku.jpg"
            },
            {
                "title": "Peruvanam Pooram",
                "description": "Temple festival featuring traditional Panchari Melam percussion orchestras and Sasthavinte Ezhunnallathu ritual dance continuing overnight.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Peruvanam Mahadeva Temple",
                "address": "Cherpu, Thrissur, Kerala 680559",
                "latitude": 10.4389,
                "longitude": 76.2031,
                "event_date": datetime(2026, 3, 27).date(),
                "start_time": time(20, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Arattupuzha_Pooram.jpg"
            },
            {
                "title": "Arattupuzha Pooram (Devamela)",
                "description": "Grand assembly of 80+ village deities on caparisoned elephants gathering in sacred confluence at the ancient temple.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Arattupuzha Sree Sastha Temple",
                "address": "Arattupuzha, Thrissur, Kerala 680547",
                "latitude": 10.4285,
                "longitude": 76.2081,
                "event_date": datetime(2026, 3, 30).date(),
                "start_time": time(23, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Arattupuzha_Pooram.jpg"
            },
            # April
            {
                "title": "Nenmara Vallangi Vela",
                "description": "Competitive fireworks festival featuring illuminated Anapanthal arches and spectacular pyrotechnics duels between temples.",
                "category": "temple",
                "district": "Palakkad",
                "venue_name": "Nellikulangara Bhagavathy Temple",
                "address": "Nenmara & Vallangi, Palakkad, Kerala 679506",
                "latitude": 10.5891,
                "longitude": 76.6025,
                "event_date": datetime(2026, 4, 3).date(),
                "start_time": time(18, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/8/87/Nenmara_Vallangi_Vela.jpg"
            },
            {
                "title": "Malayattoor Perunnal",
                "description": "Ancient pilgrimage celebrating St. Thomas with hill climbing rituals and high mountain masses at the historic shrine.",
                "category": "church",
                "district": "Ernakulam",
                "venue_name": "St. Thomas International Shrine",
                "address": "Malayattoor, Ernakulam, Kerala 682315",
                "latitude": 10.1872,
                "longitude": 76.5028,
                "event_date": datetime(2026, 4, 12).date(),
                "start_time": time(6, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/7/77/Malayattoor_church.jpg"
            },
            {
                "title": "Vishu & Vishukkani (Kerala New Year)",
                "description": "Ancient Malayalam New Year celebration starting with auspicious Vishukkani viewing and blessing rituals throughout Kerala.",
                "category": "community",
                "district": "Thrissur",
                "venue_name": "Guruvayur Sree Krishna Temple",
                "address": "Guruvayur, Thrissur, Kerala 680103",
                "latitude": 10.5946,
                "longitude": 76.0411,
                "event_date": datetime(2026, 4, 14).date(),
                "start_time": time(4, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Vishukkani_setup.jpg"
            },
            {
                "title": "Kadammanitta Padayani",
                "description": "Ritualistic folk performance featuring elaborate Kolam masks and overnight performances celebrating local deity traditions.",
                "category": "arts_culture",
                "district": "Pathanamthitta",
                "venue_name": "Kadammanitta Devi Temple",
                "address": "Kadammanitta, Pathanamthitta, Kerala 689645",
                "latitude": 9.2974,
                "longitude": 76.8122,
                "event_date": datetime(2026, 4, 14).date(),
                "start_time": time(21, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/39/Maramon_Convention.jpg"
            },
            {
                "title": "Thrissur Pooram - India's Grandest Festival",
                "description": "The world's most spectacular temple festival with caparisoned elephants, percussion orchestras, and unmatched fireworks displays.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Vadakkunnathan Temple / Thekkinkadu Maidan",
                "address": "Thrissur, Kerala 680001",
                "latitude": 10.5244,
                "longitude": 76.2137,
                "event_date": datetime(2026, 4, 26).date(),
                "start_time": time(11, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Thrissur_Pooram_1.jpg"
            },
            {
                "title": "Edathua Perunnal",
                "description": "Historic church feast featuring grand holy procession of St. George statue and solemn liturgical celebrations.",
                "category": "church",
                "district": "Alappuzha",
                "venue_name": "St. George Forane Church",
                "address": "Edathua, Alappuzha, Kerala 688524",
                "latitude": 9.3622,
                "longitude": 76.4717,
                "event_date": datetime(2026, 5, 6).date(),
                "start_time": time(9, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Edathua_church_facing_pamba_river.jpg"
            },
            {
                "title": "Puthuppally Perunnal",
                "description": "Church feast with traditional Rasa procession featuring gold and silver crosses and ancient Orthodox rituals.",
                "category": "church",
                "district": "Kottayam",
                "venue_name": "St. George Orthodox Church",
                "address": "Puthuppally, Kottayam, Kerala 686003",
                "latitude": 9.5621,
                "longitude": 76.5684,
                "event_date": datetime(2026, 5, 7).date(),
                "start_time": time(8, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Parumala_Church.jpg"
            },
            # June - August
            {
                "title": "Champakulam Moolam Boat Race",
                "description": "Ancient snake boat race featuring Chundan Vallam boats racing on sacred River Pamba during monsoon season.",
                "category": "sports",
                "district": "Alappuzha",
                "venue_name": "River Pamba",
                "address": "Champakulam, Alappuzha, Kerala 688532",
                "latitude": 9.4123,
                "longitude": 76.4182,
                "event_date": datetime(2026, 6, 29).date(),
                "start_time": time(14, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/9/90/Nehru_Trophy_Boat_Race_Alappuzha.jpg"
            },
            {
                "title": "Aanayoottu at Vadakkunnathan Temple",
                "description": "Sacred elephant feeding ritual with medicinal food balls offered inside the ancient temple courtyard.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Vadakkunnathan Temple",
                "address": "Thrissur, Kerala 680001",
                "latitude": 10.5244,
                "longitude": 76.2137,
                "event_date": datetime(2026, 7, 17).date(),
                "start_time": time(9, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Thrissur_Pooram_1.jpg"
            },
            {
                "title": "International Documentary & Short Film Festival of Kerala",
                "description": "Prestigious film festival showcasing world cinema, documentary films, and direct interactions with international filmmakers.",
                "category": "arts_culture",
                "district": "Thiruvananthapuram",
                "venue_name": "Kairali & Nila Theatre Complex",
                "address": "Thiruvananthapuram, Kerala 695001",
                "latitude": 8.4891,
                "longitude": 76.9498,
                "event_date": datetime(2026, 7, 24).date(),
                "start_time": time(9, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Kairali_Nila_Sree_Theatre_Complex.jpg"
            },
            {
                "title": "Nehru Trophy Boat Race",
                "description": "Premier championship snake boat race featuring fastest Chundan Vallam boats competing on Punnamada Lake.",
                "category": "sports",
                "district": "Alappuzha",
                "venue_name": "Punnamada Lake",
                "address": "Alappuzha, Kerala 688013",
                "latitude": 9.5036,
                "longitude": 76.3475,
                "event_date": datetime(2026, 8, 8).date(),
                "start_time": time(11, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/9/90/Nehru_Trophy_Boat_Race_Alappuzha.jpg"
            },
            {
                "title": "Athachamayam",
                "description": "Royal cultural pageant and street parade featuring Theyyam, Kathakali, and elaborate cultural floats celebrating heritage.",
                "category": "arts_culture",
                "district": "Ernakulam",
                "venue_name": "Thripunithura Royal Town",
                "address": "Thripunithura, Ernakulam, Kerala 682301",
                "latitude": 9.9482,
                "longitude": 76.3533,
                "event_date": datetime(2026, 8, 16).date(),
                "start_time": time(9, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/4/47/Athachamayam_Tripunithura.jpg"
            },
            {
                "title": "Thiruvonam (Onam Harvest Festival)",
                "description": "Kerala's grandest harvest festival celebrating prosperity with floral carpets (Pookalam), boat races, and traditional feasts statewide.",
                "category": "community",
                "district": "Thiruvananthapuram",
                "venue_name": "Statewide Kerala Celebrations",
                "address": "Kerala State",
                "latitude": 8.5241,
                "longitude": 76.9366,
                "event_date": datetime(2026, 8, 26).date(),
                "start_time": time(6, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Onam_Pookalam.jpg"
            },
            {
                "title": "Pulikali (Tiger Dance Parade)",
                "description": "Spectacular folk art street parade with hundreds of body-painted performers dancing as tigers through city streets.",
                "category": "arts_culture",
                "district": "Thrissur",
                "venue_name": "Swaraj Round",
                "address": "Thrissur, Kerala 680001",
                "latitude": 10.5244,
                "longitude": 76.2137,
                "event_date": datetime(2026, 8, 29).date(),
                "start_time": time(16, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Pulikali_Thrissur.jpg"
            },
            {
                "title": "Aranmula Valla Sadya & Boat Race",
                "description": "Sacred ritual feast with 64 traditional dishes followed by ancient Palliyodam snake boat race on River Pamba.",
                "category": "temple",
                "district": "Pathanamthitta",
                "venue_name": "Aranmula Parthasarathy Temple",
                "address": "Aranmula, Pathanamthitta, Kerala 689644",
                "latitude": 9.3328,
                "longitude": 76.6811,
                "event_date": datetime(2026, 8, 30).date(),
                "start_time": time(11, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Aranmula_Boat_Race.jpg"
            },
            # October - December
            {
                "title": "Navarathri & Vidyarambham",
                "description": "Nine-day classical music festival and child education initiation ceremony celebrating goddess Saraswathi.",
                "category": "arts_culture",
                "district": "Kottayam",
                "venue_name": "Panachikkadu Saraswathi Temple",
                "address": "Kottayam, Kerala 686001",
                "latitude": 9.5312,
                "longitude": 76.5381,
                "event_date": datetime(2026, 10, 19).date(),
                "start_time": time(17, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Onam_Pookalam.jpg"
            },
            {
                "title": "Mannarasala Ayilyam",
                "description": "Unique serpent festival with sacred Sarpabali rituals celebrating the serpent deity with traditional ceremonies.",
                "category": "temple",
                "district": "Alappuzha",
                "venue_name": "Mannarasala Sree Nagaraja Temple",
                "address": "Haripad, Alappuzha, Kerala 690534",
                "latitude": 9.2782,
                "longitude": 76.4521,
                "event_date": datetime(2026, 11, 2).date(),
                "start_time": time(14, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Chettikulangara_Bharani_Kettukazhcha.jpg"
            },
            {
                "title": "Parumala Perunnal",
                "description": "Ancient Orthodox church feast with traditional Rasa procession and solemn liturgical celebrations.",
                "category": "church",
                "district": "Pathanamthitta",
                "venue_name": "St. Peter's & St. Paul's Orthodox Church",
                "address": "Parumala, Pathanamthitta, Kerala 689651",
                "latitude": 9.3514,
                "longitude": 76.5606,
                "event_date": datetime(2026, 11, 2).date(),
                "start_time": time(8, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Parumala_Church.jpg"
            },
            {
                "title": "Kalpathi Ratholsavam",
                "description": "Historic chariot festival featuring confluence of 6 elaborately decorated wooden temple chariots in heritage village.",
                "category": "temple",
                "district": "Palakkad",
                "venue_name": "Sri Viswanatha Swamy Temple",
                "address": "Kalpathi, Palakkad, Kerala 678501",
                "latitude": 10.7858,
                "longitude": 76.6483,
                "event_date": datetime(2026, 11, 16).date(),
                "start_time": time(17, 30),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Kalpathi_Ratholsavam.jpg"
            },
            {
                "title": "Guruvayur Ekadasi",
                "description": "Sacred temple festival with all-day worship and classical music homage (Chembai Sangeetholsavam) overnight.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Guruvayur Sree Krishna Temple",
                "address": "Guruvayur, Thrissur, Kerala 680103",
                "latitude": 10.5946,
                "longitude": 76.0411,
                "event_date": datetime(2026, 11, 21).date(),
                "start_time": time(6, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Vishukkani_setup.jpg"
            },
            {
                "title": "Vaikathashtami",
                "description": "Sacred temple midnight darshan with offerings and processions featuring neighboring deities at Vaikom temple.",
                "category": "temple",
                "district": "Kottayam",
                "venue_name": "Vaikom Mahadeva Temple",
                "address": "Vaikom, Kottayam, Kerala 686141",
                "latitude": 9.7482,
                "longitude": 76.3951,
                "event_date": datetime(2026, 12, 1).date(),
                "start_time": time(0, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Arattupuzha_Pooram.jpg"
            },
            {
                "title": "Thripunithura Vrishchikotsavam",
                "description": "Month-long temple festival with gold-plated elephant processions and nightly Kathakali classical dance performances.",
                "category": "temple",
                "district": "Ernakulam",
                "venue_name": "Sree Poornathrayeesa Temple",
                "address": "Thripunithura, Ernakulam, Kerala 682301",
                "latitude": 9.9482,
                "longitude": 76.3533,
                "event_date": datetime(2026, 12, 5).date(),
                "start_time": time(10, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/4/47/Athachamayam_Tripunithura.jpg"
            },
            {
                "title": "International Film Festival of Kerala (IFFK)",
                "description": "Premier international film festival showcasing world cinema across 15 venues with filmmaker open forums.",
                "category": "arts_culture",
                "district": "Thiruvananthapuram",
                "venue_name": "Tagore Theatre & City Theatres",
                "address": "Thiruvananthapuram, Kerala 695001",
                "latitude": 8.4982,
                "longitude": 76.9531,
                "event_date": datetime(2026, 12, 11).date(),
                "start_time": time(9, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Tagore_Theatre_Trivandrum.jpg"
            },
            {
                "title": "Cochin Carnival",
                "description": "Year-end celebration featuring burning of Pappanji effigy on New Year's Eve and grand carnival rally parade.",
                "category": "community",
                "district": "Ernakulam",
                "venue_name": "Fort Kochi Vasco da Gama Square",
                "address": "Fort Kochi, Ernakulam, Kerala 682001",
                "latitude": 9.9656,
                "longitude": 76.2423,
                "event_date": datetime(2026, 12, 25).date(),
                "start_time": time(15, 0),
                "cover_image": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Aspinwall_House_Fort_Kochi.jpg"
            },
        ]

        events_created = 0
        for event_data in events_data:
            district_name = event_data.pop("district")
            district = districts.get(district_name, districts["Ernakulam"])

            # Select organizer based on district
            organizer = list(organizers.values())[events_created % len(organizers)]

            event_data["district"] = district
            event_data["status"] = "verified"
            event_data["is_featured"] = True
            event_data["organizer"] = organizer

            event, created = Event.objects.get_or_create(
                title=event_data["title"],
                event_date=event_data["event_date"],
                district=district,
                defaults=event_data
            )

            if created:
                events_created += 1
                self.stdout.write(f"✓ Created event: {event.title}")

        # Create Event Confirmations and Attendance
        all_users = list(users.values())
        for event in Event.objects.all()[:20]:
            # Add confirmations from 2-4 random users
            for user in all_users[:3]:
                EventConfirmation.objects.get_or_create(event=event, user=user)
            # Add attendance from 1-3 random users
            for user in all_users[:2]:
                Attendance.objects.get_or_create(event=event, user=user)

        self.stdout.write(self.style.SUCCESS(f"\n✅ Seed data created successfully!"))
        self.stdout.write(f"   Districts: {len(districts)}")
        self.stdout.write(f"   Event Organizers: {len(organizers)}")
        self.stdout.write(f"   Sample Users: {len(users)}")
        self.stdout.write(f"   Events: {events_created}")
        self.stdout.write(f"   All events marked as VERIFIED & FEATURED")
