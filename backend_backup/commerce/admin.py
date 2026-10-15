from django.contrib import admin
from .models import CartItem, Stock, Order, OrderItem, Reservation

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "on_hand", "reserved")
    search_fields = ("product__name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "currency", "total", "created_at", "expires_at")
    list_filter = ("status", "currency")
    readonly_fields = ("id", "user", "status", "currency", "total", "created_at", "expires_at")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("order", "stock", "quantity", "consumed", "released")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "unit_price", "quantity")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
