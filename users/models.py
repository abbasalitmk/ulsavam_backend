import hashlib
import random
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, identifier, **extra_fields):
        if not identifier:
            raise ValueError("An identifier (phone or email) is required.")
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if '@' in identifier:
            email = self.normalize_email(identifier)
            user = self.model(email=email, **extra_fields)
        else:
            user = self.model(phone_number=identifier, **extra_fields)

        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError("Superuser must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=150, default="Festival Goer")
    avatar = models.URLField(max_length=500, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    district = models.ForeignKey(
        'districts.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    is_info_revealed = models.BooleanField(default=False)
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('ml', 'Malayalam')],
        default='en'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.display_name or self.email or self.phone_number or f"User {self.id}"

class OTPRequest(models.Model):
    identifier = models.CharField(max_length=150, db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=50, default='login')
    expires_at = models.DateTimeField()
    attempt_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @staticmethod
    def generate_code():
        return f"{random.randint(100000, 999999)}"

    @staticmethod
    def hash_code(code):
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    def is_valid(self, code):
        if timezone.now() > self.expires_at:
            return False
        if self.attempt_count >= 5:
            return False
        return self.code_hash == self.hash_code(code)
