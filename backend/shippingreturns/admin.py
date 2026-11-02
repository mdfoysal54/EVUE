from django.contrib import admin
from .models import ShippingZone, ReturnRequest

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("city", "name", "fee", "active")
    list_filter = ("active",)
    search_fields = ("city", "name")

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("purchase__id", "user__email")
    readonly_fields = ("purchase", "user", "reason", "created_at", "updated_at")
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False