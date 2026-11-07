from django.urls import path

from . import views

urlpatterns = [
    path('', views.explore_view, name='explore'),
    path('search/', views.search_view, name='search'),
    path('dashboard/', views.center_dashboard, name='center_dashboard'),
    path('<int:pk>/', views.center_detail, name='center_detail'),
]