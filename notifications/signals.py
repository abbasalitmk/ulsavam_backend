from django.db.models.signals import post_save
from django.dispatch import receiver
from events.models import Event, EventConfirmation, Attendance
from users.models import User
from .models import Notification

@receiver(post_save, sender=EventConfirmation)
def notify_on_confirmation(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        confirrmer = instance.user
        
        # Notify organizer if different from confirmer
        if event.organizer and event.organizer != confirrmer:
            Notification.objects.create(
                user=event.organizer,
                type='confirmation_added',
                message=f"Someone verified your event '{event.title}'. Verified count: {event.confirmations_count}.",
                related_event=event
            )

@receiver(post_save, sender=Attendance)
def notify_on_going(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        attendee = instance.user
        
        # Notify organizer
        if event.organizer and event.organizer != attendee:
            display_name = attendee.display_name if attendee.is_info_revealed else "Someone"
            Notification.objects.create(
                user=event.organizer,
                type='new_attendee',
                message=f"{display_name} marked 'Going' to your event '{event.title}'. Total going: {event.going_count}.",
                related_event=event
            )

@receiver(post_save, sender=Event)
def notify_district_users_on_new_event(sender, instance, created, **kwargs):
    if created and instance.district:
        # Notify users residing/preferring this district
        target_users = User.objects.filter(district=instance.district).exclude(id=instance.organizer.id if instance.organizer else None)
        notifications = [
            Notification(
                user=u,
                type='district_event_added',
                message=f"New event added in {instance.district.name}: '{instance.title}'",
                related_event=instance
            )
            for u in target_users[:50]  # Limit batch for performance
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)
