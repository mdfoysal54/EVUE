from django.contrib import admin
from .collection_models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "publish_from", "publish_until", "sort_order")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("products",)
    ordering = ("sort_order", "name")