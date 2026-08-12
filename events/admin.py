from django.contrib import admin
from .models import Event, EventConfirmation, Attendance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'district', 'category', 'event_date', 'status', 'is_featured', 'confirmations_count', 'going_count')
    list_filter = ('district', 'category', 'status', 'is_featured', 'event_date')
    search_fields = ('title', 'venue_name', 'address', 'description')

@admin.register(EventConfirmation)
class EventConfirmationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'created_at')
    search_fields = ('event__title', 'user__email', 'user__phone_number')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'created_at')
    search_fields = ('event__title', 'user__email', 'user__phone_number')
