from django.contrib import admin
from django.utils import timezone
from .models import Announcement, Offer, Notification, TransactionRecord, AdminAuditLog, NewsletterSubscription

class AuditedAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        AdminAuditLog.objects.create(actor=request.user, action='update' if change else 'create', target=f'{obj._meta.label}:{obj.pk}')
    def delete_model(self, request, obj):
        AdminAuditLog.objects.create(actor=request.user, action='delete', target=f'{obj._meta.label}:{obj.pk}')
        super().delete_model(request, obj)

@admin.register(Announcement)
class AnnouncementAdmin(AuditedAdmin):
    list_display = ('title','kind','placement','published','publish_from','publish_until','priority')
    list_filter = ('published','kind','placement','important')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-priority','-created_at')
    search_fields = ('title','body')

@admin.register(Offer)
class OfferAdmin(AuditedAdmin):
    list_display = ('code','percent_off','active','starts_at','ends_at')
    list_filter = ('active',)
    search_fields = ('code',)

@admin.register(Notification)
class NotificationAdmin(AuditedAdmin):
    list_display = ('title','user','read','created_at')
    list_filter = ('read',)
    search_fields = ('title','user__username')

@admin.register(TransactionRecord)
class TransactionRecordAdmin(admin.ModelAdmin):
    list_display = ('reference','provider','amount_minor','currency','status','created_at')
    search_fields = ('reference',)
    list_filter = ('status','provider')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor','action','target','created_at')
    list_filter = ('action',)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email','consented_at','active')
    search_fields = ('email',)
    list_filter = ('active',)
    readonly_fields = ('email','consented_at')
    def has_add_permission(self, request): return False