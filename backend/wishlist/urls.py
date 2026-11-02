from django.urls import path
from .views import WishlistView, WishlistItemView

urlpatterns = [
    path("", WishlistView.as_view(), name="wishlist-list-add"),
    path("<uuid:product_id>/", WishlistItemView.as_view(), name="wishlist-remove"),
]
