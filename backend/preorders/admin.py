from django.contrib import admin
from .models import Release, PreorderRequest, WaitlistEntry

@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'state', 'opens_at', 'closes_at', 'allocation', 'reserved', 'public')
    list_filter = ('state', 'public')
    search_fields = ('product__name', 'product__slug')
    readonly_fields = ('reserved',)
    autocomplete_fields = ('product',)

@admin.register(PreorderRequest)
class PreorderRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'release', 'customer', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('release', 'customer', 'quantity', 'status', 'idempotency_key', 'created_at')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(WaitlistEntry)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ('release', 'customer', 'created_at', 'notified_at')
    readonly_fields = ('release', 'customer', 'created_at', 'notified_at')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
