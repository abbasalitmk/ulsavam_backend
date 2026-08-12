from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [
    ('temple', 'Temple Festival'),
    ('church', 'Church Feast'),
    ('dj_music', 'DJ & Music Show'),
    ('beach_meetup', 'Beach Meetup'),
    ('arts_culture', 'Arts & Culture'),
    ('food_fest', 'Food Festival'),
    ('sports', 'Sports & Games'),
    ('community', 'Community Gathering'),
]

STATUS_CHOICES = [
    ('pending', 'Pending Verification'),
    ('verified', 'Verified'),
    ('rejected', 'Rejected'),
]

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='community')
    district = models.ForeignKey(
        'districts.District',
        on_delete=models.CASCADE,
        related_name='events'
    )
    venue_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField(default=10.0)
    longitude = models.FloatField(default=76.0)
    event_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    cover_image = models.URLField(max_length=500, blank=True, null=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.district.name})"

    @property
    def confirmations_count(self):
        return self.confirmations.count()

    @property
    def going_count(self):
        return self.attendances.count()

class EventConfirmation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='confirmations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_confirmations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"Confirmation by {self.user} for {self.event.title}"

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} is going to {self.event.title}"
