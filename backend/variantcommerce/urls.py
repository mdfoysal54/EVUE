from django.urls import path
from .views import Variants,Cart,Checkout,Purchases,CancelPurchase,Preorder,CancelPreorder
urlpatterns=[
 path('products/<uuid:product_id>/variants/',Variants.as_view()),
 path('cart/',Cart.as_view()),
 path('checkout/',Checkout.as_view()),
 path('orders/',Purchases.as_view()),
 path('orders/<uuid:pk>/cancel/',CancelPurchase.as_view()),
 path('preorders/',Preorder.as_view()),
 path('preorders/<uuid:pk>/cancel/',CancelPreorder.as_view()),
]
