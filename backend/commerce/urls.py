from django.urls import path
from . import views
urlpatterns = [
    path("cart/", views.cart),
    path("orders/", views.orders),
    path("orders/<uuid:order_id>/", views.order_detail),
]