from django.urls import path
from . import views
urlpatterns = [
    path('announcements/', views.announcements),
    path('offers/', views.offers),
    path('notifications/', views.my_notifications),
    path('reports/', views.reports),
]