from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.generic import TemplateView
from users.models import User
import json


def admin_login_page(request):
    """Serve the admin login page"""
    return render(request, 'admin_panel/login.html')


class SuperAdminPanelView(TemplateView):
    """
    Serve the custom admin panel shell. Authentication is enforced
    client-side (dashboard.js checks for a JWT in localStorage and
    every /api/admin/* call requires a valid staff/superuser token) -
    there is no Django session involved, so this view does not gate on
    request.user.is_authenticated.
    """
    template_name = 'admin_panel/dashboard.html'


@csrf_exempt
@require_http_methods(["POST"])
def admin_login_api(request):
    """
    SuperAdmin panel login - email + password only, restricted to
    staff or superuser accounts.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required.'}, status=400)

    user = User.objects.filter(email=email).first()

    if not user or not user.has_usable_password() or not user.check_password(password):
        return JsonResponse({'error': 'Invalid email or password.'}, status=400)

    if not (user.is_staff or user.is_superuser):
        return JsonResponse({'error': 'This account does not have admin access.'}, status=403)

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
