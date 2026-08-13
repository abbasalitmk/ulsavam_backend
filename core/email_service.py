import logging
import requests
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _send_via_resend(to_email, subject, html_content):
    """
    Send an email via the Resend HTTPS API.

    We use Resend's HTTP API (port 443) instead of raw SMTP because
    outbound SMTP (port 587/465/25) is blocked on Render's network,
    which caused OTP emails to hang until the gunicorn worker timeout
    killed the request. HTTPS API calls aren't affected by that.
    """
    api_key = settings.RESEND_API_KEY
    if not api_key:
        logger.error("RESEND_API_KEY is not configured")
        return False

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            },
            timeout=10,
        )

        if response.status_code >= 400:
            logger.error(f"Resend API error ({response.status_code}) for {to_email}: {response.text}")
            return False

        logger.info(f"Email sent successfully to {to_email} via Resend")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to send email via Resend to {to_email}: {str(e)}")
        return False


def send_otp_email(email, otp_code, purpose='login'):
    """
    Send OTP via email with professional HTML template

    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: 'login' or 'verification'
    """
    context = {
        'otp_code': otp_code,
        'purpose': purpose,
        'validity': '10 minutes'
    }
    html_message = render_to_string('emails/otp_email.html', context)
    return _send_via_resend(email, 'Your Ulsavam OTP Code', html_message)


def send_verification_email(email, verification_link):
    """Send email verification link"""
    context = {
        'verification_link': verification_link,
        'email': email
    }
    html_message = render_to_string('emails/verification_email.html', context)
    return _send_via_resend(email, 'Verify Your Ulsavam Account', html_message)


def send_welcome_email(display_name, email):
    """Send welcome email to new user"""
    context = {
        'display_name': display_name,
        'email': email
    }
    html_message = render_to_string('emails/welcome_email.html', context)
    return _send_via_resend(email, 'Welcome to Ulsavam! 🎉', html_message)
