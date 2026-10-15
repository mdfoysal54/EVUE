from django.urls import path
from .views import public_appearance, public_flags

urlpatterns = [
    path("appearance/", public_appearance, name="public-appearance"),
    path("flags/", public_flags, name="public-flags"),
]
