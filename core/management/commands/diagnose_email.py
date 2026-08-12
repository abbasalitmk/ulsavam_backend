from django.core.management.base import BaseCommand
from django.conf import settings
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Command(BaseCommand):
    help = "Comprehensive email diagnosis - test each component separately"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*70)
        self.stdout.write("COMPREHENSIVE EMAIL DIAGNOSIS")
        self.stdout.write("="*70)

        # Step 1: Check Configuration
        self.check_configuration()

        # Step 2: Test Raw SMTP Connection
        self.test_smtp_connection()

        # Step 3: Test Django Email Backend
        self.test_django_backend()

        # Step 4: Get User Info
        self.check_recipient()

    def check_configuration(self):
        """Check all email configuration settings"""
        self.stdout.write("\n" + "-"*70)
        self.stdout.write("STEP 1: CHECKING EMAIL CONFIGURATION")
        self.stdout.write("-"*70)

        config = {
            'EMAIL_BACKEND': settings.EMAIL_BACKEND,
            'EMAIL_HOST': settings.EMAIL_HOST,
            'EMAIL_PORT': settings.EMAIL_PORT,
            'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
            'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
        }

        for key, value in config.items():
            self.stdout.write(f"  ✓ {key}: {value}")

        # Check credentials from environment
        self.stdout.write("\n📧 CREDENTIALS CHECK:")

        email_user_env = os.environ.get('EMAIL_HOST_USER')
        email_pass_env = os.environ.get('EMAIL_HOST_PASSWORD')

        email_user = settings.EMAIL_HOST_USER
        email_pass = settings.EMAIL_HOST_PASSWORD

        if email_user_env:
            self.stdout.write(f"  ✓ EMAIL_HOST_USER from environment: {email_user_env}")
        else:
            self.stdout.write(f"  ⚠️  EMAIL_HOST_USER from defaults: {email_user}")

        if email_pass_env:
            masked = email_pass_env[:4] + '*' * (len(email_pass_env) - 8) + email_pass_env[-4:]
            self.stdout.write(f"  ✓ EMAIL_HOST_PASSWORD from environment (masked): {masked}")
        else:
            if email_pass:
                masked = email_pass[:4] + '*' * (len(email_pass) - 8) + email_pass[-4:]
                self.stdout.write(f"  ⚠️  EMAIL_HOST_PASSWORD from defaults (masked): {masked}")
            else:
                self.stdout.write(f"  ❌ EMAIL_HOST_PASSWORD is NOT SET!")

        # Verify password format
        if email_pass:
            self.stdout.write(f"\n🔐 PASSWORD ANALYSIS:")
            self.stdout.write(f"    Length: {len(email_pass)} characters")
            self.stdout.write(f"    Has spaces: {'Yes' if ' ' in email_pass else 'No'}")
            if len(email_pass) != 31 and len(email_pass) != 16:  # 16 chars or 16 + 15 spaces
                self.stdout.write(f"    ⚠️  UNUSUAL LENGTH! Gmail app passwords should be 16 chars or ~31 with spaces")

    def test_smtp_connection(self):
        """Test raw SMTP connection without Django"""
        self.stdout.write("\n" + "-"*70)
        self.stdout.write("STEP 2: TESTING RAW SMTP CONNECTION")
        self.stdout.write("-"*70)

        email_user = settings.EMAIL_HOST_USER
        email_pass = settings.EMAIL_HOST_PASSWORD

        if not email_user or not email_pass:
            self.stdout.write("❌ Email credentials not configured!")
            return

        try:
            self.stdout.write(f"  Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            self.stdout.write("  ✓ Connected!")

            self.stdout.write("  Starting TLS...")
            server.starttls()
            self.stdout.write("  ✓ TLS started!")

            self.stdout.write(f"  Authenticating as {email_user}...")
            server.login(email_user, email_pass)
            self.stdout.write("  ✓ Authentication successful!")

            # Test sending a real email
            self.stdout.write("\n📨 TESTING ACTUAL EMAIL SEND:")
            test_email = input("  Enter recipient email: ").strip()

            if not test_email or '@' not in test_email:
                self.stdout.write("  ❌ Invalid email address")
                server.quit()
                return

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Ulsavam Test Email - Raw SMTP'
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = test_email

            # Plain text version
            text = "This is a test email sent via raw SMTP (not Django backend)"
            part = MIMEText(text, 'plain')
            msg.attach(part)

            # Send
            self.stdout.write(f"  Sending to {test_email}...")
            result = server.sendmail(settings.DEFAULT_FROM_EMAIL, [test_email], msg.as_string())
            self.stdout.write(f"  ✓ Email sent successfully!")
            self.stdout.write(f"    Result: {result}")

            server.quit()
            self.stdout.write("  ✓ Connection closed")

        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f"  ❌ AUTHENTICATION FAILED"))
            self.stdout.write(f"     Error: {str(e)}")
            self.stdout.write("""
     SOLUTIONS:
     1. Verify app password is EXACTLY correct (case-sensitive)
     2. Check if 2-Factor Authentication is enabled on Gmail
     3. Regenerate app password from https://myaccount.google.com/security
     4. Use full 16-character code, don't modify it
     5. Make sure password contains spaces: "ekyg xkml rdtl ddyp"
            """)

        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(f"  ❌ SMTP ERROR: {str(e)}"))

        except ConnectionError as e:
            self.stdout.write(self.style.ERROR(f"  ❌ CONNECTION ERROR: {str(e)}"))
            self.stdout.write("""
     SOLUTIONS:
     1. Check internet connection
     2. Verify EMAIL_HOST = 'smtp.gmail.com'
     3. Verify EMAIL_PORT = 587
     4. Check firewall/network settings
     5. Try from different network (mobile hotspot)
            """)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ ERROR: {type(e).__name__}: {str(e)}"))

    def test_django_backend(self):
        """Test Django's email backend"""
        self.stdout.write("\n" + "-"*70)
        self.stdout.write("STEP 3: TESTING DJANGO EMAIL BACKEND")
        self.stdout.write("-"*70)

        try:
            from django.core.mail import send_mail

            test_email = input("  Enter recipient email: ").strip()

            if not test_email or '@' not in test_email:
                self.stdout.write("  ❌ Invalid email address")
                return

            self.stdout.write(f"  Sending test email via Django to {test_email}...")

            result = send_mail(
                subject='Ulsavam Test - Django Backend',
                message='This email was sent via Django email backend (test_email command)',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )

            self.stdout.write(f"  ✓ Email sent successfully via Django!")
            self.stdout.write(f"    Result: {result}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Django backend error: {type(e).__name__}"))
            self.stdout.write(f"     {str(e)}")

    def check_recipient(self):
        """Check database for user email"""
        self.stdout.write("\n" + "-"*70)
        self.stdout.write("STEP 4: CHECKING DATABASE USERS")
        self.stdout.write("-"*70)

        try:
            from users.models import User

            users = User.objects.filter(email__isnull=False).exclude(email='')
            self.stdout.write(f"\n✓ Total users with emails: {users.count()}")

            if users.count() > 0:
                self.stdout.write("\nUsers in database:")
                for user in users[:10]:  # Show first 10
                    self.stdout.write(f"  - {user.display_name}: {user.email} (Staff: {user.is_staff})")

                if users.count() > 10:
                    self.stdout.write(f"  ... and {users.count() - 10} more")

        except Exception as e:
            self.stdout.write(f"❌ Error querying users: {str(e)}")


class EmailTesterMixin:
    """Helper mixin for manual testing"""

    @staticmethod
    def test_manual():
        """Manual step-by-step testing"""
        print("\n" + "="*70)
        print("MANUAL EMAIL TEST")
        print("="*70)

        # Test 1: Direct SMTP
        print("\n1. Testing direct SMTP connection...")
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
            print("   ✓ Can reach smtp.gmail.com:587")
            server.quit()
        except Exception as e:
            print(f"   ❌ Cannot reach server: {e}")
            return

        # Test 2: Auth
        print("\n2. Testing authentication...")
        email_user = input("   Email: ").strip()
        email_pass = input("   App Password: ").strip()

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_pass)
            print("   ✓ Authentication successful!")
            server.quit()
        except smtplib.SMTPAuthenticationError:
            print("   ❌ Authentication FAILED - check credentials")
            return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return

        # Test 3: Send email
        print("\n3. Testing email send...")
        recipient = input("   Recipient email: ").strip()

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_pass)

            msg = f"Subject: Test\n\nThis is a test email"
            server.sendmail(email_user, [recipient], msg)
            print(f"   ✓ Email sent to {recipient}")
            server.quit()
        except Exception as e:
            print(f"   ❌ Send failed: {e}")
