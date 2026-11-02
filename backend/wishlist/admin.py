from django.contrib import admin
from .models import WishlistItem

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "product", "created_at")
    list_select_related = ("customer", "product")
    search_fields = ("product__name",)
    readonly_fields = ("customer", "product", "created_at")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
