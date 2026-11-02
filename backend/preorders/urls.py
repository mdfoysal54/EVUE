from django.urls import path
from .views import PublicReleases, Reserve, Cancel, JoinWaitlist
urlpatterns = [
    path('releases/', PublicReleases.as_view(), name='preorder-releases'),
    path('reserve/', Reserve.as_view(), name='preorder-reserve'),
    path('requests/<uuid:pk>/cancel/', Cancel.as_view(), name='preorder-cancel'),
    path('releases/<int:pk>/waitlist/', JoinWaitlist.as_view(), name='preorder-waitlist'),
]
