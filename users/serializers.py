from rest_framework import serializers
from .models import User
from districts.serializers import DistrictSerializer
from districts.models import District

class UserSerializer(serializers.ModelSerializer):
    district_details = DistrictSerializer(source='district', read_only=True)
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'display_name', 'avatar',
            'district', 'district_details', 'is_info_revealed',
            'preferred_language', 'created_at'
        ]
        read_only_fields = ['id', 'phone_number', 'email', 'created_at']

class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    method = serializers.ChoiceField(choices=['phone', 'email'], required=True)

class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    code = serializers.CharField(required=True, max_length=6, min_length=6)

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
