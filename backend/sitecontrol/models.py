from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify


class MediaAsset(models.Model):
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to="site-assets/%Y/%m/", validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "gif"])])
    alt_text = models.CharField(max_length=250, blank=True)
    folder = models.CharField(max_length=80, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title


class SiteTheme(models.Model):
    name = models.CharField(max_length=80, unique=True, default="Default")
    active = models.BooleanField(default=False)
    logo = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="logo_themes")
    favicon = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="favicon_themes")
    primary_color = models.CharField(max_length=7, default="#171717")
    background_color = models.CharField(max_length=7, default="#ffffff")
    text_color = models.CharField(max_length=7, default="#171717")
    font_family = models.CharField(max_length=100, default="Arial, sans-serif")
    default_mode = models.CharField(max_length=5, choices=[("light", "Light"), ("dark", "Dark")], default="light")
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name


class SectionAppearance(models.Model):
    page = models.SlugField(max_length=100, help_text="home, shop, about, etc.")
    section = models.SlugField(max_length=100, help_text="hero, featured, story, etc.")
    heading = models.CharField(max_length=240, blank=True)
    subtitle = models.TextField(blank=True)
    desktop_background = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="desktop_sections")
    mobile_background = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="mobile_sections")
    dark_background = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="dark_sections")
    overlay_opacity = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["page", "section"], name="unique_site_section")]
        ordering = ["page", "section"]
    def __str__(self): return f"{self.page} / {self.section}"


class ContentPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField(blank=True)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.title


class FeatureFlag(models.Model):
    key = models.SlugField(unique=True)
    description = models.CharField(max_length=250, blank=True)
    enabled = models.BooleanField(default=False)
    rollout_percent = models.PositiveSmallIntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    def __str__(self): return self.key


class SiteSetting(models.Model):
    key = models.SlugField(unique=True)
    value = models.TextField(blank=True)
    public = models.BooleanField(default=False, help_text="Only mark harmless settings as public; never store secrets here.")
    def __str__(self): return self.key
