import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.throttling import OTPRequestThrottle, LoginThrottle
from core.email_service import send_otp_email
from .models import User, OTPRequest
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    OTPRequestSerializer, OTPVerifySerializer, LogoutSerializer
)

logger = logging.getLogger(__name__)


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class RegisterView(APIView):
    """
    Register a new account with email and/or phone, name, password, dob,
    gender, district, and an optional profile picture.
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = tokens_for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'message': 'Registration successful.',
            **tokens,
            'user': user_data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login with username (email or phone number) + password.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username'].strip()
        password = serializer.validated_data['password']

        if '@' in username:
            user = User.objects.filter(email=username.lower()).first()
        else:
            user = User.objects.filter(phone_number=username).first()

        if not user:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.has_usable_password() or not user.check_password(password):
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

        tokens = tokens_for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'message': 'Login successful.',
            **tokens,
            'user': user_data
        }, status=status.HTTP_200_OK)


class OTPRequestView(APIView):
    """
    Request an OTP for login (email delivery). Only works for
    identifiers that already have a registered account.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPRequestThrottle]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier'].strip()
        method = serializer.validated_data['method']

        if method == 'email':
            user_exists = User.objects.filter(email=identifier.lower()).exists()
        else:
            user_exists = User.objects.filter(phone_number=identifier).exists()

        if not user_exists:
            return Response(
                {'error': 'No account found with this identifier. Please register first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        code = OTPRequest.generate_code()
        code_hash = OTPRequest.hash_code(code)
        expires_at = timezone.now() + timedelta(minutes=10)

        OTPRequest.objects.create(
            identifier=identifier,
            code_hash=code_hash,
            purpose='login',
            expires_at=expires_at
        )

        if method == 'email' and '@' in identifier:
            email_sent = send_otp_email(identifier, code, purpose='login')
            if not email_sent:
                return Response(
                    {'error': 'Failed to send OTP email. Please try again.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # For SMS or other methods, log to console for development
            print(f"\n==========================================")
            print(f"[ULSAVAM OTP] {method.upper()}: {identifier}")
            print(f"CODE: {code}")
            print(f"==========================================\n")
            logger.info(f"Generated OTP for {identifier}: {code}")

        return Response({
            'message': f'OTP sent successfully to {identifier}.',
            'validity': 'Valid for 10 minutes'
        }, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    """
    Verify OTP and log in. Requires an existing registered account
    (does not auto-create users) - use /api/auth/register/ to sign up.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier'].strip()
        code = serializer.validated_data['code'].strip()

        otp_obj = OTPRequest.objects.filter(identifier=identifier).order_by('-created_at').first()

        if not otp_obj:
            return Response({'error': 'No OTP request found for this identifier.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.attempt_count += 1
        otp_obj.save()

        if not otp_obj.is_valid(code):
            return Response({'error': 'Invalid or expired OTP code.'}, status=status.HTTP_400_BAD_REQUEST)

        if '@' in identifier:
            user = User.objects.filter(email=identifier.lower()).first()
        else:
            user = User.objects.filter(phone_number=identifier).first()

        if not user:
            return Response(
                {'error': 'No account found with this identifier. Please register first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        tokens = tokens_for_user(user)
        user_data = UserSerializer(user, context={'request': request}).data

        return Response({
            'message': 'Login successful.',
            **tokens,
            'user': user_data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change the authenticated user's password. current_password is
    required unless the account has no password set yet.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveUpdateAPIView):
    """
    Get or update the authenticated user's profile, including
    uploading/replacing the profile picture (multipart/form-data).
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user
