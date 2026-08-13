from rest_framework import serializers
from .models import Event, EventConfirmation, Attendance, EventImage
from districts.serializers import DistrictSerializer
from districts.models import District


class EventImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = EventImage
        fields = ['id', 'image_url', 'order', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

class EventListSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    confirmations_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)
    is_going = serializers.SerializerMethodField()
    is_confirmed_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'district', 'district_name', 'district_slug',
            'venue_name', 'event_date', 'start_time', 'cover_image', 'status',
            'is_featured', 'confirmations_count', 'going_count', 'is_going',
            'is_confirmed_by_user', 'created_at'
        ]

    def get_is_going(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Attendance.objects.filter(event=obj, user=request.user).exists()
        return False

    def get_is_confirmed_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EventConfirmation.objects.filter(event=obj, user=request.user).exists()
        return False

class EventDetailSerializer(serializers.ModelSerializer):
    district_details = DistrictSerializer(source='district', read_only=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())
    organizer_name = serializers.SerializerMethodField()
    confirmations_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)
    is_going = serializers.SerializerMethodField()
    is_confirmed_by_user = serializers.SerializerMethodField()
    images = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'district', 'district_details',
            'venue_name', 'address', 'latitude', 'longitude', 'event_date', 'start_time',
            'cover_image', 'images', 'organizer', 'organizer_name', 'status', 'is_featured',
            'confirmations_count', 'going_count', 'is_going', 'is_confirmed_by_user',
            'created_at'
        ]
        read_only_fields = ['id', 'organizer', 'status', 'created_at']

    def get_organizer_name(self, obj):
        if not obj.organizer:
            return "Community Member"
        if obj.organizer.is_info_revealed or (self.context.get('request') and self.context['request'].user == obj.organizer):
            return obj.organizer.display_name or "Organizer"
        return "Anonymous Organizer"

    def get_is_going(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Attendance.objects.filter(event=obj, user=request.user).exists()
        return False

    def get_is_confirmed_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EventConfirmation.objects.filter(event=obj, user=request.user).exists()
        return False

class AttendeeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    display_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'user_id', 'display_name', 'avatar', 'created_at']

    def get_display_name(self, obj):
        user = obj.user
        request = self.context.get('request')
        if user.is_info_revealed or (request and request.user == user):
            return user.display_name or f"User_{user.id}"
        return "Anonymous Festival Goer"

    def get_avatar(self, obj):
        user = obj.user
        request = self.context.get('request')
        if user.is_info_revealed or (request and request.user == user):
            return user.avatar or ""
        return ""
