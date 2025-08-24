from django.urls import path, include
from django.contrib.auth import views as auth_views
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from . import views

# Custom Authentication Form that uses email instead of username
class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'

app_name = 'restaurant'

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),
    
    # Menu Views
    path('menu/', views.modern_menu, name='menu'),  # Main menu page
    path('menu/legacy/', views.menu_list, name='legacy_menu'),  # Kept for backward compatibility
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Cart API Endpoints
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/update/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Order History
    path('orders/', views.order_history, name='order_history'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='restaurant/registration/login.html',
        redirect_authenticated_user=True,
        authentication_form=EmailAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='restaurant:menu'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='restaurant/registration/password_reset_form.html',
        email_template_name='restaurant/registration/password_reset_email.html',
        subject_template_name='restaurant/registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='restaurant/registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='restaurant/registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='restaurant/registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Debug URLs
    path('debug/menu/', views.debug_menu_items, name='debug_menu'),
]
