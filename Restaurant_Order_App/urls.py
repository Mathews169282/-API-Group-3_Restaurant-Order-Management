# Hotel_Order_App/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('orders/', views.Order_list, name='order_list'),
    path('orders/new/', views.Order_create, name='order_create'),
    path('orders/<int:pk>/', views.Order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.Order_edit, name='order_edit'),
    path('menu/', views.Menu_list, name='menu_list'),
]
