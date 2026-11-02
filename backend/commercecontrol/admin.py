from django.contrib import admin
from .models import (
    AuditEvent,
    CourierEvent,
    CourierShipment,
    PrivateAccess,
    RefundCase,
    ShippingQuote,
    VIPProfile,
)


@admin.register(ShippingQuote)
class ShippingQuoteAdmin(admin.ModelAdmin):
    list_display = ("purchase", "city_snapshot", "fee", "grand_total", "created_at")
    readonly_fields = (
        "purchase",
        "zone",
        "city_snapshot",
        "fee",
        "merchandise_total",
        "grand_total",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RefundCase)
class RefundCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase", "amount", "state", "approved_by", "created_at")
    readonly_fields = (
        "approved_by",
        "gateway_reference",
        "gateway_response",
        "created_at",
        "updated_at",
    )

    def get_readonly_fields(self, request, obj=None):
        base_readonly = self.readonly_fields
        if obj:
            return base_readonly + ("purchase", "amount", "reason", "state")
        return base_readonly + ("state",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CourierShipment)
class CourierShipmentAdmin(admin.ModelAdmin):
    list_display = ("delivery", "provider", "external_id", "tracking_number")


@admin.register(CourierEvent)
class CourierEventAdmin(admin.ModelAdmin):
    list_display = ("shipment", "external_event_id", "event_type", "received_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivateAccess)
class PrivateAccessAdmin(admin.ModelAdmin):
    pass


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "object_ref", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False