from django.urls import path
from .views import ShippingQuote, CustomerReturns

urlpatterns = [
    path("shipping/quote/", ShippingQuote.as_view(), name="evu-shipping-quote"),
    path("returns/", CustomerReturns.as_view(), name="evu-customer-returns"),
]