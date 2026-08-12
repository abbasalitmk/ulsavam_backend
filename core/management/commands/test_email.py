from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Test email configuration and send test OTP email"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("EMAIL CONFIGURATION TEST")
        self.stdout.write("=" * 60)

        # Check configuration
        self.stdout.write("\n📧 EMAIL SETTINGS:")
        self.stdout.write(f"  Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"  Port: {settings.EMAIL_PORT}")
        self.stdout.write(f"  Use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  Default From: {settings.DEFAULT_FROM_EMAIL}")

        self.stdout.write("\n🔑 CREDENTIALS:")
        email_user = os.environ.get('EMAIL_HOST_USER', 'abbasalitmk@gmail.com')
        email_password = os.environ.get('EMAIL_HOST_PASSWORD', '')

        self.stdout.write(f"  EMAIL_HOST_USER: {email_user}")
        if email_password:
            # Show masked password
            masked = email_password[:5] + '*' * (len(email_password) - 10) + email_password[-5:]
            self.stdout.write(f"  EMAIL_HOST_PASSWORD: {masked}")
        else:
            self.stdout.write("  EMAIL_HOST_PASSWORD: ⚠️  NOT SET!")

        # Check if credentials are from environment or defaults
        self.stdout.write("\n⚙️  ENVIRONMENT VARIABLES:")
        if os.environ.get('EMAIL_HOST_USER'):
            self.stdout.write("  ✅ EMAIL_HOST_USER is set in environment")
        else:
            self.stdout.write("  ⚠️  EMAIL_HOST_USER NOT in environment (using default)")

        if os.environ.get('EMAIL_HOST_PASSWORD'):
            self.stdout.write("  ✅ EMAIL_HOST_PASSWORD is set in environment")
        else:
            self.stdout.write("  ⚠️  EMAIL_HOST_PASSWORD NOT in environment (using default)")

        # Try to send test email
        self.stdout.write("\n📨 SENDING TEST EMAIL:")
        test_email = input("Enter your email address to test: ").strip()

        if not test_email or '@' not in test_email:
            self.stdout.write(self.style.ERROR("❌ Invalid email address"))
            return

        try:
            # Send simple test email
            self.stdout.write("  Attempting to send test email...")

            send_mail(
                subject='Ulsavam OTP Test Email',
                message='This is a test email from Ulsavam backend.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Test email sent successfully to {test_email}!"))
            self.stdout.write("   Check your inbox (and spam folder) for the email.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {str(e)}"))
            self.stdout.write("\n🔧 TROUBLESHOOTING:")

            if "Authentication failed" in str(e) or "535" in str(e):
                self.stdout.write("""
  Issue: Gmail authentication failed
  Solution:
    1. Verify app password is correct (16-character code)
    2. Ensure 2-Factor Authentication is enabled on Gmail
    3. Check that app password is from "App passwords" section
    4. Try regenerating app password if too old
    5. Add to Render environment variables:
       - EMAIL_HOST_USER: abbasalitmk@gmail.com
       - EMAIL_HOST_PASSWORD: your_16_char_app_password
""")
            elif "Connection refused" in str(e) or "timed out" in str(e):
                self.stdout.write("""
  Issue: Cannot connect to Gmail SMTP server
  Solution:
    1. Check internet connection
    2. Verify EMAIL_HOST = 'smtp.gmail.com'
    3. Verify EMAIL_PORT = 587
    4. Verify EMAIL_USE_TLS = True
    5. Check firewall/VPN settings
    6. Try from different network if possible
""")
            elif "SMTPException" in str(e):
                self.stdout.write(f"""
  Issue: SMTP error occurred
  Details: {str(e)}
  Solution:
    1. Verify all email settings are correct
    2. Check if credentials are set in environment
    3. Test credentials on another tool (e.g., Thunderbird)
    4. Check Gmail account for suspicious activity alerts
""")
            else:
                self.stdout.write(f"""
  Issue: {type(e).__name__}
  Details: {str(e)}
  Solution:
    1. Check all email configuration settings
    2. Verify environment variables on Render
    3. Review Django logs for more details
    4. Check Gmail account security settings
""")

        # Test OTP email template
        self.stdout.write("\n📧 TESTING OTP EMAIL TEMPLATE:")
        try:
            context = {
                'otp_code': '123456',
                'purpose': 'login',
                'validity': '10 minutes'
            }
            html_message = render_to_string('emails/otp_email.html', context)
            plain_message = strip_tags(html_message)

            self.stdout.write("  ✅ OTP email template renders successfully")
            self.stdout.write(f"  HTML length: {len(html_message)} characters")
            self.stdout.write(f"  Plain text length: {len(plain_message)} characters")
        except Exception as e:
            self.stdout.write(f"  ❌ Error rendering template: {str(e)}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("EMAIL TEST COMPLETE")
        self.stdout.write("=" * 60)
