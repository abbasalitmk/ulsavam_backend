from rest_framework import serializers
from users.models import User
from districts.models import District
from events.models import Event, EventConfirmation, Attendance


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user management"""
    district_name = serializers.CharField(source='district.name', read_only=True)
    confirmation_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'display_name', 'district',
            'district_name', 'preferred_language', 'is_staff', 'is_superuser',
            'created_at', 'confirmation_count', 'attendance_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_confirmation_count(self, obj):
        return obj.event_confirmations.count()

    def get_attendance_count(self, obj):
        return obj.attendances.count()


class AdminDistrictSerializer(serializers.ModelSerializer):
    """Serializer for admin district management"""
    event_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = ['id', 'name', 'slug', 'event_count', 'user_count']
        read_only_fields = ['id', 'slug']

    def get_event_count(self, obj):
        return obj.events.count()

    def get_user_count(self, obj):
        return obj.users.count()


class AdminEventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for event list view"""
    district_name = serializers.CharField(source='district.name', read_only=True)
    organizer_name = serializers.CharField(source='organizer.display_name', read_only=True)
    confirmation_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'district', 'district_name',
            'event_date', 'start_time', 'status', 'is_featured',
            'organizer_name', 'confirmation_count', 'attendance_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_confirmation_count(self, obj):
        return obj.confirmations.count()

    def get_attendance_count(self, obj):
        return obj.attendances.count()


class AdminEventDetailSerializer(serializers.ModelSerializer):
    """Complete serializer for event detail view"""
    district_name = serializers.CharField(source='district.name', read_only=True)
    organizer_email = serializers.CharField(source='organizer.email', read_only=True)
    organizer_name = serializers.CharField(source='organizer.display_name', read_only=True)
    confirmation_count = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    confirmations = serializers.SerializerMethodField()
    attendances = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'district', 'district_name',
            'venue_name', 'address', 'latitude', 'longitude', 'event_date',
            'start_time', 'cover_image', 'organizer', 'organizer_email', 'organizer_name',
            'status', 'is_featured', 'created_at', 'confirmation_count',
            'attendance_count', 'confirmations', 'attendances'
        ]
        read_only_fields = ['id', 'created_at']

    def get_confirmation_count(self, obj):
        return obj.confirmations.count()

    def get_attendance_count(self, obj):
        return obj.attendances.count()

    def get_confirmations(self, obj):
        confirmations = EventConfirmation.objects.filter(event=obj).select_related('user')
        return [
            {
                'id': c.id,
                'user_id': c.user.id,
                'user_name': c.user.display_name,
                'user_email': c.user.email,
                'created_at': c.created_at
            }
            for c in confirmations
        ]

    def get_attendances(self, obj):
        attendances = Attendance.objects.filter(event=obj).select_related('user')
        return [
            {
                'id': a.id,
                'user_id': a.user.id,
                'user_name': a.user.display_name,
                'user_email': a.user.email,
                'created_at': a.created_at
            }
            for a in attendances
        ]
