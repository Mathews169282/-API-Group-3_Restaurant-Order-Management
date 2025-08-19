from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
]
