from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'two_factor_enabled', 'created_at')
    list_filter = ('two_factor_enabled',)
    search_fields = ('user__username', 'user__email')