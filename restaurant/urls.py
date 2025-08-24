from django.urls import path, include
from django.contrib.auth import views as auth_views
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from . import views
from . import views_order_management

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
    
    # Enhanced Order Management
    path('orders/create/', views_order_management.create_order_view, name='create_order'),
    path('orders/<int:order_id>/', views_order_management.order_detail_view, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views_order_management.update_order_status_view, name='update_order_status'),
    path('orders/<int:order_id>/cancel/', views_order_management.cancel_order_view, name='cancel_order'),
    
    # Kitchen Management
    path('kitchen/queue/', views_order_management.kitchen_queue_view, name='kitchen_queue'),
    path('kitchen/orders/<int:order_id>/preparing/', views_order_management.mark_order_preparing, name='mark_order_preparing'),
    path('kitchen/orders/<int:order_id>/ready/', views_order_management.mark_order_ready, name='mark_order_ready'),
    
    # Order Status Views
    path('orders/ready/', views_order_management.ready_orders_view, name='ready_orders'),
    path('orders/pending/', views_order_management.pending_orders_view, name='pending_orders'),
    path('tables/<int:table_id>/orders/', views_order_management.table_orders_view, name='table_orders'),
    
    # API Endpoints for AJAX
    path('api/kitchen/queue/', views_order_management.api_kitchen_queue, name='api_kitchen_queue'),
    path('api/orders/<int:order_id>/status/', views_order_management.api_order_status, name='api_order_status'),
    path('api/tables/<int:table_id>/status/', views_order_management.api_table_status, name='api_table_status'),
    
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
