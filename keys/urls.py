from django.urls import path
from . import views

app_name = 'keys'

urlpatterns = [
    path('assign-sales-person/<int:vehicle_id>/', views.assign_sales_person, name='assign-sales-person'),
    path('key-tracking/', views.key_tracking, name='key-tracking'),
    path('mark-key-returned/<int:checkout_id>/', views.mark_key_returned, name='mark-key-returned'),
] 