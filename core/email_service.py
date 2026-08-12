from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_otp_email(email, otp_code, purpose='login'):
    """
    Send OTP via email with professional HTML template

    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: 'login' or 'verification'
    """
    try:
        subject = 'Your Ulsavam OTP Code'

        context = {
            'otp_code': otp_code,
            'purpose': purpose,
            'validity': '10 minutes'
        }

        html_message = render_to_string('emails/otp_email.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email='Ulsavam <noreply@ulsavam.com>',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"OTP email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def send_verification_email(email, verification_link):
    """Send email verification link"""
    try:
        subject = 'Verify Your Ulsavam Account'

        context = {
            'verification_link': verification_link,
            'email': email
        }

        html_message = render_to_string('emails/verification_email.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email='Ulsavam <noreply@ulsavam.com>',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification email sent to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False


def send_welcome_email(display_name, email):
    """Send welcome email to new user"""
    try:
        subject = 'Welcome to Ulsavam! 🎉'

        context = {
            'display_name': display_name,
            'email': email
        }

        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email='Ulsavam <noreply@ulsavam.com>',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False
