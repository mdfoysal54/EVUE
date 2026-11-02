from django.urls import path
from . import views
urlpatterns = [
    path('shipping/lock/', views.lock_shipping, name='cc_shipping_lock'),
    path('courier/webhook/', views.courier_webhook, name='cc_courier_webhook'),
]
