import hashlib
import re
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import SiteTheme, SectionAppearance, FeatureFlag

COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def asset_url(request, asset):
    if not asset or not asset.file:
        return None
    return request.build_absolute_uri(asset.file.url)


@require_GET
def public_appearance(request):
    theme = SiteTheme.objects.filter(active=True).order_by("pk").first()
    sections = SectionAppearance.objects.filter(enabled=True).select_related("desktop_background", "mobile_background", "dark_background")
    theme_data = None
    if theme:
        theme_data = {
            "logo": asset_url(request, theme.logo),
            "favicon": asset_url(request, theme.favicon),
            "primary_color": theme.primary_color if COLOR.fullmatch(theme.primary_color) else "#171717",
            "background_color": theme.background_color if COLOR.fullmatch(theme.background_color) else "#ffffff",
            "text_color": theme.text_color if COLOR.fullmatch(theme.text_color) else "#171717",
            "default_mode": theme.default_mode,
        }
    return JsonResponse({
        "theme": theme_data,
        "sections": [{
            "page": s.page, "section": s.section, "heading": s.heading,
            "subtitle": s.subtitle, "overlay_opacity": s.overlay_opacity,
            "desktop_background": asset_url(request, s.desktop_background),
            "mobile_background": asset_url(request, s.mobile_background),
            "dark_background": asset_url(request, s.dark_background),
        } for s in sections],
    })


@require_GET
def public_flags(request):
    result = {}
    for flag in FeatureFlag.objects.all():
        # Anonymous clients receive only global flags. Percentage rollouts need
        # authenticated, stable identity and server-side enforcement.
        result[flag.key] = flag.enabled and flag.rollout_percent == 100
    return JsonResponse({"flags": result})
