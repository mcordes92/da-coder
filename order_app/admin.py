from django.contrib import admin
from .models import Orders


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    """Admin configuration for Orders model."""
    list_display = ('id', 'offer_detail', 'customer_user', 'business_user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('customer_user__username', 'business_user__username', 'offer_detail__title')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('offer_detail', 'customer_user', 'business_user')
