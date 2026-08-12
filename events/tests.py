import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from districts.models import District
from users.models import User
from events.models import Event, EventConfirmation, Attendance

@pytest.mark.django_db
class TestEventsAndConfirmationGate:
    def setup_method(self):
        self.client = APIClient()
        self.district = District.objects.create(name='Thrissur')
        self.user1 = User.objects.create_user(identifier='user1@ulsavam.in', display_name='User One')
        self.user2 = User.objects.create_user(identifier='user2@ulsavam.in', display_name='User Two')
        self.user3 = User.objects.create_user(identifier='user3@ulsavam.in', display_name='User Three')
        self.user4 = User.objects.create_user(identifier='user4@ulsavam.in', display_name='User Four')

    def test_create_event_starts_as_pending(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('event-list')
        payload = {
            'title': 'Thrissur Local Festival',
            'description': 'A vibrant community temple gathering in Thrissur maidan.',
            'category': 'temple',
            'district': self.district.id,
            'venue_name': 'Swaraj Round',
            'address': 'Thrissur, Kerala',
            'event_date': '2026-08-10',
            'start_time': '16:00:00',
        }
        res = self.client.post(url, payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['status'] == 'pending'

    def test_three_confirmation_gate_auto_flips_to_verified(self):
        # Create pending event
        event = Event.objects.create(
            title='Beach Volleyball Fest',
            description='Community sports event',
            category='sports',
            district=self.district,
            venue_name='Chavakkad Beach',
            address='Chavakkad',
            event_date='2026-08-15',
            organizer=self.user1,
            status='pending'
        )

        confirm_url = reverse('event-confirm', kwargs={'pk': event.id})

        # 1st confirmation
        self.client.force_authenticate(user=self.user1)
        r1 = self.client.post(confirm_url)
        assert r1.status_code == status.HTTP_201_CREATED
        event.refresh_from_db()
        assert event.status == 'pending'
        assert event.confirmations_count == 1

        # 2nd confirmation
        self.client.force_authenticate(user=self.user2)
        r2 = self.client.post(confirm_url)
        assert r2.status_code == status.HTTP_201_CREATED
        event.refresh_from_db()
        assert event.status == 'pending'
        assert event.confirmations_count == 2

        # 3rd confirmation -> AUTO FLIPS TO VERIFIED!
        self.client.force_authenticate(user=self.user3)
        r3 = self.client.post(confirm_url)
        assert r3.status_code == status.HTTP_201_CREATED
        event.refresh_from_db()
        assert event.status == 'verified'
        assert event.confirmations_count == 3

    def test_going_toggle(self):
        event = Event.objects.create(
            title='Music Concert',
            description='Live fusion music',
            category='dj_music',
            district=self.district,
            venue_name='Town Hall',
            address='Thrissur',
            event_date='2026-08-20',
            organizer=self.user1,
            status='verified'
        )
        going_url = reverse('event-going', kwargs={'pk': event.id})

        self.client.force_authenticate(user=self.user1)
        res1 = self.client.post(going_url)
        assert res1.status_code == status.HTTP_200_OK
        assert res1.data['is_going'] is True

        res2 = self.client.post(going_url)
        assert res2.status_code == status.HTTP_200_OK
        assert res2.data['is_going'] is False

    def test_attendees_privacy_masking(self):
        event = Event.objects.create(
            title='Private Gathering',
            description='Community meet',
            category='community',
            district=self.district,
            venue_name='Hall A',
            address='Thrissur',
            event_date='2026-08-25',
            status='verified'
        )
        # user1 has is_info_revealed = False
        self.user1.is_info_revealed = False
        self.user1.save()
        Attendance.objects.create(event=event, user=self.user1)

        attendees_url = reverse('event-attendees', kwargs={'pk': event.id})
        # Unauthenticated request (guest viewing attendees)
        self.client.logout()
        res = self.client.get(attendees_url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data[0]['display_name'] == "Anonymous Festival Goer"
