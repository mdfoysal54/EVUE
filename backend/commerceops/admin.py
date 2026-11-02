from django.contrib import admin
from .models import OperationsAlert, NotificationOutbox

@admin.register(OperationsAlert)
class OperationsAlertAdmin(admin.ModelAdmin):
    list_display = ("key", "severity", "category", "active", "last_seen")
    list_filter = ("severity", "category", "active")
    search_fields = ("key", "detail")
    readonly_fields = ("key", "severity", "category", "detail", "first_seen", "last_seen")
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(NotificationOutbox)
class NotificationOutboxAdmin(admin.ModelAdmin):
    list_display = ("event_key", "recipient_email", "status", "attempts", "created_at")
    list_filter = ("status",)
    search_fields = ("event_key", "recipient_email")
    readonly_fields = ("event_key", "recipient_email", "subject", "body", "status", "attempts", "last_error", "created_at", "sent_at")
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
