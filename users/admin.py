from django.contrib import admin
from .models import User, OTPRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'email', 'phone_number', 'district', 'is_info_revealed', 'created_at')
    search_fields = ('display_name', 'email', 'phone_number')
    list_filter = ('district', 'is_info_revealed', 'preferred_language')

@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'identifier', 'expires_at', 'attempt_count', 'created_at')
    search_fields = ('identifier',)
