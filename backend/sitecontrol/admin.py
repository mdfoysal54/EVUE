from django.contrib import admin
from django.utils.html import format_html
from .models import MediaAsset, SiteTheme, SectionAppearance, ContentPage, FeatureFlag, SiteSetting


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "folder", "preview", "created_at")
    search_fields = ("title", "alt_text", "folder")
    readonly_fields = ("preview", "created_at")
    def preview(self, obj):
        if obj.pk and obj.file:
            return format_html('<img src="{}" alt="" style="max-width:180px;max-height:120px;object-fit:contain">', obj.file.url)
        return "No image"


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "default_mode", "updated_at")
    list_editable = ("active",)


@admin.register(SectionAppearance)
class SectionAppearanceAdmin(admin.ModelAdmin):
    list_display = ("page", "section", "enabled", "updated_at")
    list_filter = ("page", "enabled")
    search_fields = ("page", "section", "heading")


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "published", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "body")
    list_filter = ("published",)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled", "rollout_percent")


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "public")
    list_filter = ("public",)
