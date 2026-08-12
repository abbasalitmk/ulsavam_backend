from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
import json


def admin_login_page(request):
    """Serve the admin login page"""
    return render(request, 'admin_panel/login.html')


class SuperAdminPanelView(TemplateView):
    """Serve the custom admin panel"""
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get admin token for API calls
        context['admin_user'] = self.request.user if self.request.user.is_authenticated else None
        return context

    def get(self, request, *args, **kwargs):
        # Check if user is staff
        if not request.user.is_authenticated or not request.user.is_staff:
            return render(request, 'admin_panel/login.html', status=401)

        return super().get(request, *args, **kwargs)


@csrf_exempt
@require_http_methods(["POST"])
def admin_login_api(request):
    """API endpoint for admin panel login"""
    try:
        data = json.loads(request.body)
        identifier = data.get('identifier')
        code = data.get('code')

        if not identifier or not code:
            return JsonResponse({'error': 'Missing identifier or code'}, status=400)

        # Use the OTP verification flow
        from users.models import OTPRequest
        from rest_framework_simplejwt.tokens import RefreshToken

        otp_obj = OTPRequest.objects.filter(identifier=identifier).order_by('-created_at').first()

        if not otp_obj:
            return JsonResponse({'error': 'No OTP request found'}, status=400)

        otp_obj.attempt_count += 1
        otp_obj.save()

        if not otp_obj.is_valid(code):
            return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)

        # Get or create user
        if '@' in identifier:
            user, _ = User.objects.get_or_create(email=identifier.lower())
        else:
            user, _ = User.objects.get_or_create(phone_number=identifier)

        # Check if user is staff
        if not user.is_staff:
            return JsonResponse({'error': 'User is not an admin'}, status=403)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
