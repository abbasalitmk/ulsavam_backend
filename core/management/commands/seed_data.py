from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from districts.models import District
from users.models import User
from events.models import Event, EventConfirmation, Attendance


class Command(BaseCommand):
    help = "Seed the database with Kerala-related events and users"

    def handle(self, *args, **options):
        self.stdout.write("Starting data seeding...")

        # Create Districts
        districts_data = [
            "Thiruvananthapuram", "Kollam", "Alappuzha", "Kottayam",
            "Idukki", "Ernakulam", "Thrissur", "Palakkad",
            "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
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

        # Create Sample Users
        sample_users_data = [
            ("user1@example.com", "Raj Kumar", "Thiruvananthapuram"),
            ("user2@example.com", "Priya Sharma", "Kochi"),
            ("user3@example.com", "Amit Patel", "Kozhikode"),
            ("user4@example.com", "Anjali Nair", "Thrissur"),
            ("user5@example.com", "Deepak Menon", "Malappuram"),
            ("festival_lover@example.com", "Festival Enthusiast", "Ernakulam"),
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

        # Kerala Festival Events Data
        events_data = [
            {
                "title": "Thrissur Pooram Festival",
                "description": "India's most spectacular temple festival featuring caparisoned elephants, percussion orchestras, and cultural performances.",
                "category": "temple",
                "district": "Thrissur",
                "venue_name": "Vadakkunnathan Temple",
                "address": "Temple Road, Thrissur, Kerala 680001",
                "latitude": 10.5236,
                "longitude": 76.2137,
                "event_date": datetime.now().date() + timedelta(days=30),
                "start_time": "18:00"
            },
            {
                "title": "Cochin Carnivale",
                "description": "A vibrant celebration of Kochi's multicultural heritage with music, dance, art exhibitions, and street performances.",
                "category": "arts_culture",
                "district": "Ernakulam",
                "venue_name": "Fort Kochi Parade Ground",
                "address": "Fort Kochi, Ernakulam, Kerala 682001",
                "latitude": 9.9626,
                "longitude": 76.2437,
                "event_date": datetime.now().date() + timedelta(days=45),
                "start_time": "17:00"
            },
            {
                "title": "Biennale Kochi",
                "description": "International contemporary art festival showcasing artworks from artists around the world.",
                "category": "arts_culture",
                "district": "Ernakulam",
                "venue_name": "Various venues in Kochi",
                "address": "Fort Kochi, Ernakulam, Kerala",
                "latitude": 9.9626,
                "longitude": 76.2437,
                "event_date": datetime.now().date() + timedelta(days=60),
                "start_time": "10:00"
            },
            {
                "title": "Attukal Pongala Festival",
                "description": "The world's largest congregation of women gathering to prepare ritual dishes as an offering to Goddess Attukal Bhagavathy.",
                "category": "temple",
                "district": "Thiruvananthapuram",
                "venue_name": "Attukal Bhagavathy Temple",
                "address": "Attukal, Thiruvananthapuram, Kerala 695001",
                "latitude": 8.5241,
                "longitude": 76.9366,
                "event_date": datetime.now().date() + timedelta(days=15),
                "start_time": "09:00"
            },
            {
                "title": "Palolem Beach Meetup",
                "description": "Sunset gathering at Palolem beach with music, bonfire, and a community of beach lovers. Connect with fellow travelers.",
                "category": "beach_meetup",
                "district": "Thiruvananthapuram",
                "venue_name": "Palolem Beach",
                "address": "Palolem, Thiruvananthapuram, Kerala 695501",
                "latitude": 8.3868,
                "longitude": 76.3119,
                "event_date": datetime.now().date() + timedelta(days=5),
                "start_time": "17:30"
            },
            {
                "title": "Alleppey Food Festival",
                "description": "Celebrate Kerala's culinary heritage with traditional dishes, cooking demonstrations, and food stalls.",
                "category": "food_fest",
                "district": "Alappuzha",
                "venue_name": "Alleppey Beach Convention Center",
                "address": "Alappuzha Beach Road, Kerala 688015",
                "latitude": 9.4867,
                "longitude": 76.3289,
                "event_date": datetime.now().date() + timedelta(days=25),
                "start_time": "11:00"
            },
            {
                "title": "Kottayam Bible Convention",
                "description": "Annual Christian gathering with spiritual sessions, music, and community fellowship.",
                "category": "community",
                "district": "Kottayam",
                "venue_name": "C.M.S Convention Grounds",
                "address": "Kottayam, Kerala 686001",
                "latitude": 9.5631,
                "longitude": 76.5158,
                "event_date": datetime.now().date() + timedelta(days=35),
                "start_time": "08:00"
            },
            {
                "title": "Idukki Pepper Festival",
                "description": "Agricultural festival celebrating Kerala's spice heritage with workshops and market exhibitions.",
                "category": "community",
                "district": "Idukki",
                "venue_name": "Idukki Agricultural Complex",
                "address": "Idukki Town, Kerala 685501",
                "latitude": 9.9123,
                "longitude": 76.7339,
                "event_date": datetime.now().date() + timedelta(days=40),
                "start_time": "09:00"
            },
            {
                "title": "DJ Night at Fort Kochi",
                "description": "Electric evening with top DJs performing latest hits. Dance floor open till late night.",
                "category": "dj_music",
                "district": "Ernakulam",
                "venue_name": "The Pavilion Restaurant & Bar",
                "address": "Fort Kochi, Ernakulam, Kerala 682001",
                "latitude": 9.9626,
                "longitude": 76.2437,
                "event_date": datetime.now().date() + timedelta(days=10),
                "start_time": "21:00"
            },
            {
                "title": "Thrissur Sand Sculpture Festival",
                "description": "International sand art competition showcasing incredible sand sculptures at Shornur.",
                "category": "arts_culture",
                "district": "Thrissur",
                "venue_name": "Shornur River Beach",
                "address": "Shornur, Thrissur, Kerala 680611",
                "latitude": 10.7876,
                "longitude": 76.5264,
                "event_date": datetime.now().date() + timedelta(days=50),
                "start_time": "08:00"
            },
            {
                "title": "Malappuram Book Festival",
                "description": "Celebrate the love for reading with book launches, author meetings, and literary discussions.",
                "category": "community",
                "district": "Malappuram",
                "venue_name": "Convention Hall, Malappuram",
                "address": "Malappuram City Center, Kerala 676501",
                "latitude": 10.8282,
                "longitude": 76.5055,
                "event_date": datetime.now().date() + timedelta(days=55),
                "start_time": "10:00"
            },
            {
                "title": "Kozhikode Beach Cleanup Drive",
                "description": "Community initiative to clean up Kozhikode beach. All volunteers welcome!",
                "category": "community",
                "district": "Kozhikode",
                "venue_name": "Kozhikode Beach",
                "address": "Kozhikode Beach, Kerala 673001",
                "latitude": 11.2588,
                "longitude": 75.7804,
                "event_date": datetime.now().date() + timedelta(days=12),
                "start_time": "06:00"
            },
            {
                "title": "Wayanad Adventure Sports Festival",
                "description": "Rock climbing, paragliding, and mountain biking competitions in scenic Wayanad hills.",
                "category": "sports",
                "district": "Wayanad",
                "venue_name": "Chembra Peak Area",
                "address": "Wayanad, Kerala 673591",
                "latitude": 11.4957,
                "longitude": 75.9119,
                "event_date": datetime.now().date() + timedelta(days=48),
                "start_time": "07:00"
            },
            {
                "title": "Kannur Beach Festival",
                "description": "Coastal celebration featuring water sports, beach games, and seafood food stalls.",
                "category": "food_fest",
                "district": "Kannur",
                "venue_name": "Kannur Beach",
                "address": "Kannur Beach, Kerala 670001",
                "latitude": 12.1401,
                "longitude": 75.3766,
                "event_date": datetime.now().date() + timedelta(days=42),
                "start_time": "09:00"
            },
            {
                "title": "Kasaragod Spice Market Festival",
                "description": "Celebration of the spice trade with exhibitions, tasting sessions, and cultural programs.",
                "category": "food_fest",
                "district": "Kasaragod",
                "venue_name": "Fort Square, Kasaragod",
                "address": "Kasaragod Town, Kerala 671541",
                "latitude": 12.4968,
                "longitude": 75.1419,
                "event_date": datetime.now().date() + timedelta(days=60),
                "start_time": "10:00"
            },
            {
                "title": "Palakkad Fort Music Festival",
                "description": "Classical Indian music festival showcasing Carnatic and Hindustani traditions.",
                "category": "dj_music",
                "district": "Palakkad",
                "venue_name": "Palakkad Fort Grounds",
                "address": "Palakkad Fort, Kerala 678001",
                "latitude": 10.7867,
                "longitude": 76.7236,
                "event_date": datetime.now().date() + timedelta(days=38),
                "start_time": "18:00"
            },
            {
                "title": "Kollam Boat Race Championship",
                "description": "Traditional snake boat race featuring high-speed boats and cheering crowds.",
                "category": "sports",
                "district": "Kollam",
                "venue_name": "Ashtamudi Lake",
                "address": "Ashtamudi Lake, Kollam, Kerala 691506",
                "latitude": 9.2380,
                "longitude": 76.6022,
                "event_date": datetime.now().date() + timedelta(days=28),
                "start_time": "08:00"
            },
            {
                "title": "Ernakulam Book Bazaar",
                "description": "Huge collection of books at discounted prices. Perfect for book lovers!",
                "category": "community",
                "district": "Ernakulam",
                "venue_name": "Kochi Exhibition Centre",
                "address": "Kochi, Ernakulam, Kerala 682036",
                "latitude": 9.8965,
                "longitude": 76.2839,
                "event_date": datetime.now().date() + timedelta(days=20),
                "start_time": "09:00"
            },
        ]

        events_created = 0
        for event_data in events_data:
            district_name = event_data.pop("district")
            district = districts.get(district_name, districts["Ernakulam"])

            start_time = event_data.pop("start_time")
            from datetime import time
            start_time = datetime.strptime(start_time, "%H:%M").time()

            event_data["district"] = district
            event_data["start_time"] = start_time
            event_data["status"] = "verified"
            event_data["is_featured"] = True
            event_data["organizer"] = admin_user

            event, created = Event.objects.get_or_create(
                title=event_data["title"],
                district=district,
                defaults=event_data
            )

            if created:
                events_created += 1
                self.stdout.write(f"✓ Created event: {event.title}")

        # Create Event Confirmations
        for event in Event.objects.all()[:10]:
            for user in list(users.values())[:3]:
                EventConfirmation.objects.get_or_create(
                    event=event,
                    user=user
                )

        self.stdout.write(self.style.SUCCESS(f"\n✅ Seed data created successfully!"))
        self.stdout.write(f"   Districts: {len(districts)}")
        self.stdout.write(f"   Users: {len(users) + 1}")  # +1 for admin
        self.stdout.write(f"   Events: {events_created}")
