from django.contrib import admin
from .models import Category, Product
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','currency','active','featured')
    list_filter = ('active','featured','category')
    search_fields = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}