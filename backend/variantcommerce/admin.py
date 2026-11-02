from django.contrib import admin
from .models import Variant,Location,Inventory,VariantCartItem,Purchase,PurchaseLine,PreorderAllocation,VariantPreorder
@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display=('sku','product','size','color','price','active')
    list_filter=('active','product__category')
    search_fields=('sku','product__name')
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display=('code','name','active')
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display=('variant','location','on_hand','reserved')
    list_filter=('location',)
    search_fields=('variant__sku',)
@admin.register(PreorderAllocation)
class PreorderAllocationAdmin(admin.ModelAdmin):
    list_display=('release','variant','capacity','reserved')
    readonly_fields=('reserved',)
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display=('id','user','status','total','currency','created_at')
    readonly_fields=('user','status','total','currency','idempotency_key','created_at','expires_at')
    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
@admin.register(PurchaseLine)
class PurchaseLineAdmin(admin.ModelAdmin):
    list_display=('purchase','variant','inventory','quantity','released','consumed')
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
@admin.register(VariantPreorder)
class VariantPreorderAdmin(admin.ModelAdmin):
    list_display=('id','user','allocation','quantity','status')
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
