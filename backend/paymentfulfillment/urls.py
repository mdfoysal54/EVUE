from django.urls import path
from .views import StartPayment, GatewayIPN, GatewayReturn, OrderTracking
urlpatterns = [
    path('orders/<uuid:purchase_id>/pay/', StartPayment.as_view(), name='evu-start-payment'),
    path('orders/<uuid:purchase_id>/tracking/', OrderTracking.as_view(), name='evu-order-tracking'),
    path('payments/ipn/', GatewayIPN.as_view(), name='evu-payment-ipn'),
    path('payments/return/', GatewayReturn.as_view(), name='evu-payment-return'),
]
