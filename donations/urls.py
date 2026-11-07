from django.urls import path

from . import views

urlpatterns = [
    path('donate/<int:center_id>/', views.donate_view, name='donate'),
    path('confirmation/<int:pk>/', views.confirmation_view, name='donation_confirmation'),
    path('track/', views.track_view, name='track'),
    path('history/', views.history_view, name='history'),
]