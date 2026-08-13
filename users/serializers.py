from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
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
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'email', 'display_name', 'avatar',
            'profile_pic', 'profile_pic_url', 'date_of_birth', 'gender',
            'district', 'district_details', 'is_info_revealed',
            'preferred_language', 'created_at'
        ]
        read_only_fields = ['id', 'phone_number', 'email', 'created_at']
        extra_kwargs = {
            'profile_pic': {'write_only': True, 'required': False}
        }

    def get_profile_pic_url(self, obj):
        request = self.context.get('request')
        if obj.profile_pic and hasattr(obj.profile_pic, 'url'):
            url = obj.profile_pic.url
            return request.build_absolute_uri(url) if request else url
        return obj.avatar or None


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    name = serializers.CharField(source='display_name', required=True, max_length=150)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=True)
    profile_pic = serializers.ImageField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=User._meta.get_field('gender').choices, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'phone_number', 'password', 'name',
            'date_of_birth', 'gender', 'profile_pic', 'district'
        ]

    def validate(self, attrs):
        email = attrs.get('email') or None
        phone_number = attrs.get('phone_number') or None

        if not email and not phone_number:
            raise serializers.ValidationError(
                {'error': 'Either email or phone_number must be provided.'}
            )

        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': 'This email is already registered.'})
            attrs['email'] = email

        if phone_number:
            phone_number = phone_number.strip()
            if User.objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError({'phone_number': 'This phone number is already registered.'})
            attrs['phone_number'] = phone_number

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Login with username (email or phone number) + password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


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
