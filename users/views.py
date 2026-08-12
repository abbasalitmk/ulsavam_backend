import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.throttling import OTPRequestThrottle
from .models import User, OTPRequest
from .serializers import (
    UserSerializer, OTPRequestSerializer, OTPVerifySerializer, LogoutSerializer
)

logger = logging.getLogger(__name__)

class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPRequestThrottle]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_validate_or_400 = serializer.is_valid()
        if not serializer.is_validate_or_400:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip()
        method = serializer.validated_data['method']

        code = OTPRequest.generate_code()
        code_hash = OTPRequest.hash_code(code)
        expires_at = timezone.now() + timedelta(minutes=5)

        OTPRequest.objects.create(
            identifier=identifier,
            code_hash=code_hash,
            expires_at=expires_at
        )

        # Console logging / developer delivery mode for OTP
        print(f"\n==========================================")
        print(f"[ULSAVAM DEV OTP] {method.upper()}: {identifier} -> CODE: {code}")
        print(f"==========================================\n")
        logger.info(f"Generated OTP for {identifier}: {code}")

        return Response({
            'message': f'OTP sent successfully to {identifier}.',
            'dev_hint': code  # Included for convenient testing
        }, status=status.HTTP_200_OK)

class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip()
        code = serializer.validated_data['code'].strip()

        otp_obj = OTPRequest.objects.filter(identifier=identifier).order_by('-created_at').first()

        if not otp_obj:
            return Response({'error': 'No OTP request found for this identifier.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.attempt_count += 1
        otp_obj.save()

        if not otp_obj.is_valid(code):
            return Response({'error': 'Invalid or expired OTP code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or create user
        if '@' in identifier:
            user, created = User.objects.get_or_create(email=identifier.lower())
        else:
            user, created = User.objects.get_or_create(phone_number=identifier)

        if created:
            user.display_name = f"User_{identifier[-4:]}"
            user.save()

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
