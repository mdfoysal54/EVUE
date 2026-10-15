from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

admin.site.site_header = "EVU Enterprise Administration"
admin.site.site_title = "EVU Admin"
admin.site.index_title = "Operations & Content Control"


def health(_request):
    return JsonResponse({"status": "ok", "service": "evu-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/commerce/", include("commerce.urls")),
    path("api/health/", health),
    path("api/operations/", include("operations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)