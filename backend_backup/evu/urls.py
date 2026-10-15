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
]