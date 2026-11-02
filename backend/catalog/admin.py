from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "category", "price", "currency", "active", "featured")
    list_filter = ("active", "featured", "category")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)
    fields = (
        "category", "name", "slug", "description", "price", "currency",
        "image", "image_url", "image_preview", "featured", "active",
    )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj or not obj.pk:
            return "Save a product to see its image preview."
        url = obj.image.url if obj.image else obj.image_url
        if not url:
            return "No image"
        return format_html('<img src="{}" alt="Product preview" style="max-width:320px;max-height:220px;object-fit:contain;border-radius:4px;" />', url)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        url = obj.image.url if obj.image else obj.image_url
        if not url:
            return "—"
        return format_html('<img src="{}" alt="" style="width:52px;height:52px;object-fit:cover;border-radius:3px;" />', url)

from . import collection_admin  # Register curated collections in existing Django admin.