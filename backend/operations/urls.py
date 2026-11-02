from django.urls import path
from . import views
urlpatterns = [
    path('announcements/', views.announcements),
    path('announcements/<slug:slug>/', views.announcement_detail),
    path('newsletter/subscribe/', views.subscribe_newsletter),
    path('offers/', views.offers),
    path('notifications/', views.my_notifications),
    path('reports/', views.reports),
]