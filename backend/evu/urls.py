from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def health(_request):
    return JsonResponse({"status": "ok", "service": "evu-api"})

admin.site.site_header = 'EVU Enterprise Administration'
admin.site.site_title = 'EVU Admin'
admin.site.index_title = 'Operations & Content Control'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('api/catalog/', include('catalog.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/operations/', include('operations.urls')),
    
    path("api/commerce/", include("commerce.urls")),
    path("api/preorders/", include("preorders.urls")),
    path("api/wishlist/", include("wishlist.urls")),
    path("api/v2/", include("variantcommerce.urls")),
    path('api/', include('paymentfulfillment.urls')),
    path("api/", include("shippingreturns.urls")),
    path('api/commerce-control/', include('commercecontrol.urls')),
    
    
]
# Local-only media serving. Production should use a dedicated media server or object storage.
if settings.DEBUG or settings.EVU_SERVE_MEDIA_LOCALLY:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
