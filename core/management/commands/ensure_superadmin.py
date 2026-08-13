import os
import secrets
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Idempotently promote a given email to staff+superuser, setting a password if it doesn't have one yet"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email', default=os.environ.get('SUPERADMIN_EMAIL', 'abbasalitmk@gmail.com')
        )
        parser.add_argument(
            '--password', default=os.environ.get('SUPERADMIN_PASSWORD', '')
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'display_name': 'Super Admin'}
        )

        changed = False
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        generated_password = None
        # Note: a freshly created user's `password` field defaults to ''
        # (not None), and Django's has_usable_password() treats '' as
        # "usable" (only None / the '!'-prefixed marker count as
        # unusable) - so we must also check for the empty-string case
        # explicitly, or a brand new account silently ends up with no
        # working password at all.
        if not user.password or not user.has_usable_password():
            generated_password = password or secrets.token_urlsafe(12)
            user.set_password(generated_password)
            changed = True

        if changed:
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created superadmin account: {email}"))
        else:
            self.stdout.write(f"✓ Superadmin account already existed: {email}")

        self.stdout.write(f"   is_staff={user.is_staff} is_superuser={user.is_superuser}")

        if generated_password:
            self.stdout.write(self.style.WARNING(
                f"   Password was not set - generated one: {generated_password}\n"
                f"   (Login with this once, then change it via /api/auth/me/ or Django admin.)"
            ))
