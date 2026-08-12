from django.core.management.base import BaseCommand
from districts.models import District

KERALA_DISTRICTS = [
    "Thiruvananthapuram",
    "Kollam",
    "Pathanamthitta",
    "Alappuzha",
    "Kottayam",
    "Idukki",
    "Ernakulam",
    "Thrissur",
    "Palakkad",
    "Malappuram",
    "Kozhikode",
    "Wayanad",
    "Kannur",
    "Kasaragod"
]

class Command(BaseCommand):
    help = "Seed the 14 districts of Kerala into the database."

    def handle(self, *args, **options):
        count = 0
        for name in KERALA_DISTRICTS:
            district, created = District.objects.get_or_create(name=name)
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} new districts. Total: {District.objects.count()}"))
