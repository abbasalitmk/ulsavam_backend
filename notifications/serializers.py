from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='related_event.title', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'message', 'related_event', 'event_title', 'is_read', 'created_at']
        read_only_fields = ['id', 'type', 'message', 'related_event', 'event_title', 'created_at']
