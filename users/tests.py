import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User, OTPRequest

@pytest.mark.django_db
class TestAuthAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_otp_request_and_verify_flow(self):
        # 1. Request OTP
        req_url = reverse('otp-request')
        response = self.client.post(req_url, {'identifier': 'devtest@ulsavam.kerala.in', 'method': 'email'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'dev_hint' in response.data
        otp_code = response.data['dev_hint']

        # 2. Verify OTP and receive JWT pair
        ver_url = reverse('otp-verify')
        ver_response = self.client.post(ver_url, {'identifier': 'devtest@ulsavam.kerala.in', 'code': otp_code}, format='json')
        assert ver_response.status_code == status.HTTP_200_OK
        assert 'access' in ver_response.data
        assert 'refresh' in ver_response.data
        assert ver_response.data['user']['email'] == 'devtest@ulsavam.kerala.in'

    def test_invalid_otp_fails(self):
        req_url = reverse('otp-request')
        self.client.post(req_url, {'identifier': '+919876543210', 'method': 'phone'}, format='json')

        ver_url = reverse('otp-verify')
        ver_response = self.client.post(ver_url, {'identifier': '+919876543210', 'code': '000000'}, format='json')
        assert ver_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_blacklists_refresh_token(self):
        user = User.objects.create_user(identifier='logoutuser@ulsavam.in')
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        logout_url = reverse('logout')
        res = self.client.post(logout_url, {'refresh': str(refresh)}, format='json')
        assert res.status_code == status.HTTP_205_RESET_CONTENT
