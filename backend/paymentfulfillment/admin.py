from django.contrib import admin
from .models import PaymentAttempt, Delivery, DeliveryEvent

@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = ('transaction_id','purchase','amount','currency','status','created_at')
    search_fields = ('transaction_id', 'purchase__id')
    readonly_fields = ('purchase','transaction_id','validation_id','gateway_session','status','amount','currency','verified_at','created_at')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

class DeliveryEventInline(admin.TabularInline):
    model = DeliveryEvent
    extra = 0
    readonly_fields = ('status','note','created_at')
    def has_add_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('purchase','recipient','city','status','courier','tracking_number')
    list_filter = ('status','city')
    search_fields = ('purchase__id','recipient','tracking_number')
    readonly_fields = ('purchase','recipient','phone','address','city','postal_code')
    inlines = [DeliveryEventInline]
    def has_add_permission(self, request): return False
    def save_model(self, request, obj, form, change):
        prior = Delivery.objects.get(pk=obj.pk) if change else None
        super().save_model(request,obj,form,change)
        if prior and prior.status != obj.status:
            DeliveryEvent.objects.create(delivery=obj,status=obj.status,note='Updated by staff')
