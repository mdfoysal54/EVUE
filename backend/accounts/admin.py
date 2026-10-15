from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import CustomerProfile

User = get_user_model()
admin.site.unregister(User)

class ProfileInline(admin.StackedInline):
    model = CustomerProfile
    extra = 0
    can_delete = False

@admin.register(User)
class SecureUserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline]
    actions = ["block_customers", "unblock_customers"]

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Block selected customer accounts")
    def block_customers(self, request, queryset):
        eligible = queryset.filter(is_superuser=False, is_staff=False).exclude(pk=request.user.pk)
        count = eligible.update(is_active=False)
        self.message_user(request, f"Blocked {count} customer accounts", messages.WARNING)

    @admin.action(description="Unblock selected customer accounts")
    def unblock_customers(self, request, queryset):
        eligible = queryset.filter(is_superuser=False, is_staff=False)
        count = eligible.update(is_active=True)
        self.message_user(request, f"Unblocked {count} customer accounts", messages.SUCCESS)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "verification_status", "updated_at")
    list_filter = ("verification_status",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "updated_at")
    actions = ["verify_profiles", "reject_profiles"]

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Mark selected profiles as verified")
    def verify_profiles(self, request, queryset):
        self.message_user(request, f"Verified {queryset.update(verification_status=CustomerProfile.Verification.VERIFIED)} profiles")

    @admin.action(description="Reject selected verification requests")
    def reject_profiles(self, request, queryset):
        self.message_user(request, f"Rejected {queryset.update(verification_status=CustomerProfile.Verification.REJECTED)} profiles")