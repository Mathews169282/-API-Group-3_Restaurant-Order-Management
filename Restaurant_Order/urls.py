from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Restaurant_Order_App.urls')),  # Example app include
    ]