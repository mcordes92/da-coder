from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Profile model."""
    list_display = ('user', 'type', 'first_name', 'last_name', 'location', 'tel', 'created_at')
    list_filter = ('type', 'created_at', 'location')
    search_fields = ('user__username', 'first_name', 'last_name', 'location', 'tel')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
