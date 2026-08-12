from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from districts.models import District
from users.models import User
from events.models import Event, EventConfirmation, Attendance

class Command(BaseCommand):
    help = "Seed realistic Kerala festival and event data."

    def handle(self, *args, **options):
        districts = {d.name: d for d in District.objects.all()}
        if not districts:
            self.stdout.write(self.style.ERROR("No districts found! Run seed_districts first."))
            return

        # Seed realistic test users
        users = []
        for i in range(1, 6):
            u, _ = User.objects.get_or_create(
                email=f"user{i}@ulsavam.kerala.in",
                defaults={
                    'display_name': f"Malayali Festival Goer {i}",
                    'is_info_revealed': (i % 2 == 0),
                    'district': districts.get('Thrissur') or list(districts.values())[0]
                }
            )
            users.append(u)

        today = timezone.now().date()

        demo_events = [
            {
                "title": "Thrissur Pooram 2026 - Main Kudamattam",
                "description": "The mother of all temple festivals in Kerala. Spectacular elephant line-up, vibrant parasol exchanges (Kudamattam), and traditional Ilanjithara Melam percussion ensemble at Vadakkunnathan Temple grounds.",
                "category": "temple",
                "district": districts.get("Thrissur", list(districts.values())[0]),
                "venue_name": "Vadakkunnathan Temple Grounds, Thekkinkadu Maidan",
                "address": "Swaraj Round, Thrissur, Kerala 680001",
                "latitude": 10.5244,
                "longitude": 76.2137,
                "event_date": today,
                "start_time": "15:30:00",
                "cover_image": "https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=1200&q=80",
                "status": "verified",
                "is_featured": True
            },
            {
                "title": "Neon Nights DJ Music Fest",
                "description": "An electrifying night of modern EDM, Malayalam pop remixes, dynamic laser lighting, and live food pop-ups featuring top Kerala DJs.",
                "category": "dj_music",
                "district": districts.get("Kozhikode", list(districts.values())[0]),
                "venue_name": "Calicut Trade Centre",
                "address": "Mini Bypass Rd, Swapnagari, Kozhikode, Kerala 673006",
                "latitude": 11.2625,
                "longitude": 75.7925,
                "event_date": today,
                "start_time": "18:00:00",
                "cover_image": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
                "status": "verified",
                "is_featured": True
            },
            {
                "title": "Kozhikode Sunset Beach Cleanup & Sulaimani Meetup",
                "description": "Join local environmentalists and youth for a clean beach drive followed by hot piping Sulaimani tea and live acoustic guitar jam at sunset.",
                "category": "beach_meetup",
                "district": districts.get("Kozhikode", list(districts.values())[0]),
                "venue_name": "Kozhikode South Beach",
                "address": "Beach Rd, Kozhikode, Kerala 673032",
                "latitude": 11.2483,
                "longitude": 75.7725,
                "event_date": today,
                "start_time": "16:30:00",
                "cover_image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "status": "verified",
                "is_featured": False
            },
            {
                "title": "Arthunkal Perunnal (St. Andrew's Feast)",
                "description": "Annual feast of St. Andrew's Basilica in Arthunkal, Alappuzha. Millions of devotees assemble for the sacred procession and coastal candlelight night market.",
                "category": "church",
                "district": districts.get("Alappuzha", list(districts.values())[0]),
                "venue_name": "St. Andrew's Basilica, Arthunkal",
                "address": "Arthunkal, Cherthala, Alappuzha, Kerala 688530",
                "latitude": 9.6865,
                "longitude": 76.2891,
                "event_date": today + timedelta(days=3),
                "start_time": "17:00:00",
                "cover_image": "https://images.unsplash.com/photo-1548625149-fc4a29cf7092?auto=format&fit=crop&w=1200&q=80",
                "status": "verified",
                "is_featured": True
            },
            {
                "title": "Malabar Food & Malabar Song Fest",
                "description": "Authentic Kozhikode Biryani, Unnakaya, Chattipathiri stalls accompanied by traditional Mappila Pattu live vocal performances.",
                "category": "food_fest",
                "district": districts.get("Malappuram", list(districts.values())[0]),
                "venue_name": "Kottakkunnu Park",
                "address": "Kottakkunnu, Malappuram, Kerala 676505",
                "latitude": 11.0742,
                "longitude": 76.0736,
                "event_date": today + timedelta(days=5),
                "start_time": "11:00:00",
                "cover_image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
                "status": "verified",
                "is_featured": False
            },
            {
                "title": "Kochi Biennale Community Art Gathering",
                "description": "Interactive street art exhibition, mural painting workshops, and contemporary installations in Fort Kochi heritage alleys.",
                "category": "arts_culture",
                "district": districts.get("Ernakulam", list(districts.values())[0]),
                "venue_name": "Aspinwall House, Fort Kochi",
                "address": "1/142, River Rd, Fort Kochi, Kochi, Kerala 682001",
                "latitude": 9.9675,
                "longitude": 76.2428,
                "event_date": today + timedelta(days=7),
                "start_time": "10:00:00",
                "cover_image": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1200&q=80",
                "status": "pending",
                "is_featured": False
            }
        ]

        created_count = 0
        for ev_data in demo_events:
            event, created = Event.objects.get_or_create(
                title=ev_data["title"],
                defaults={**ev_data, "organizer": users[0]}
            )
            if created:
                created_count += 1
                # Add sample confirmations & attendances
                for u in users[:3]:
                    EventConfirmation.objects.get_or_create(event=event, user=u)
                for u in users[:4]:
                    Attendance.objects.get_or_create(event=event, user=u)

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} events with sample confirmations & attendees."))
