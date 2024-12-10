from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales-performance/', views.sales_performance, name='sales-performance'),
    path('vehicle-analytics/', views.vehicle_analytics, name='vehicle-analytics'),
    path('key-analytics/', views.key_analytics, name='key-analytics'),
] 