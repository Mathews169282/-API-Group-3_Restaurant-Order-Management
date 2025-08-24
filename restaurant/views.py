from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import models, connection
from django.db.models import Count, Sum, Prefetch
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
import json

from .models import MenuCategory, MenuItem, Order, OrderItem, Table, Customer
from .forms import CustomUserCreationForm

def home(request):
    """Homepage view"""
    # Get featured categories (you can add a 'featured' field to MenuCategory model later)
    featured_categories = MenuCategory.objects.filter(is_active=True).order_by('?')[:3]  # Random 3 categories for now
    
    # Get cart data from session
    cart = request.session.get('cart', {})
    cart_data = get_cart_data(cart)
    
    context = {
        'featured_categories': featured_categories,
        'cart_item_count': cart_data['item_count'],
        'cart_data': json.dumps(cart_data, cls=DjangoJSONEncoder)
    }
    return render(request, 'restaurant/home.html', context)

def menu_list(request):
    """Legacy menu list view - kept for backward compatibility"""
    return redirect('restaurant:menu')

def modern_menu(request):
    """Modern menu view with enhanced UI"""
    # Debug: Print all categories and items
    all_categories = MenuCategory.objects.all()
    print("All Categories:", [c.name for c in all_categories])
    
    # Get active categories with their active items
    categories = []
    for category in all_categories:
        items = category.items.filter(is_active=True).order_by('name')
        if items.exists():
            categories.append({
                'id': category.id,
                'name': category.name,
                'items': items
            })
    
    print(f"Found {len(categories)} active categories with items")
    
    # Get cart data from session
    cart = request.session.get('cart', {})
    cart_data = get_cart_data(cart)
    item_count = cart_data['item_count']
    
    from django.conf import settings
    context = {
        'categories': categories,
        'cart_item_count': item_count,
        'cart_data': json.dumps(cart_data, cls=DjangoJSONEncoder),
        'MEDIA_URL': settings.MEDIA_URL
    }
    return render(request, 'restaurant/menu_list_clean.html', context)

@login_required
def dashboard(request):
    # Get or create customer for the logged-in user
    from .models import Customer
    
    try:
        customer = Customer.objects.get(email=request.user.email)
    except Customer.DoesNotExist:
        # Create a new customer if one doesn't exist
        customer = Customer.objects.create(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            phone=request.user.phone or ''
        )
    
    # Get recent orders for the customer
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    # Get order statistics
    total_orders = Order.objects.filter(customer=customer).count()
    total_spent = Order.objects.filter(
        customer=customer, 
        status=Order.Status.COMPLETED
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    # Get favorite categories
    favorite_categories = MenuCategory.objects.filter(
        items__order_items__order__customer=customer
    ).annotate(
        order_count=Count('items__order_items')
    ).order_by('-order_count')[:3] if total_orders > 0 else []
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'favorite_categories': favorite_categories,
    }
    return render(request, 'restaurant/dashboard.html', context)

def get_cart_data(cart):
    """Helper function to get cart data with item details"""
    if not cart:
        return {'items': {}, 'total': 0, 'item_count': 0}
        
    cart_items = {}
    total = 0
    item_count = 0
    
    # Get items from database
    items = MenuItem.objects.filter(id__in=cart.keys(), is_active=True)
    
    for item in items:
        quantity = cart.get(str(item.id), 0)
        if quantity > 0:
            item_total = float(item.price) * quantity
            cart_items[str(item.id)] = {
                'id': str(item.id),
                'name': item.name,
                'price': str(item.price),
                'quantity': quantity,
                'total': item_total
            }
            total += item_total
            item_count += quantity
    
    return {
        'items': cart_items,
        'total': total,
        'item_count': item_count
    }

@require_POST
def add_to_cart(request):
    """Add an item to the cart"""
    try:
        data = json.loads(request.body)
        item_id = str(data.get('item_id'))
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)
            
        # Get or initialize cart in session
        cart = request.session.get('cart', {})
        cart[item_id] = cart.get(item_id, 0) + quantity
        request.session['cart'] = cart
        
        # Get updated cart data
        cart_data = get_cart_data(cart)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Item added to cart',
            'cart_item_count': cart_data['item_count'],
            'cart_data': cart_data
        })
        
    except (ValueError, json.JSONDecodeError) as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Item ID is required'
            }, status=400)
        
        # Get cart from session
        cart = request.session.get('cart', {})
        
        # Remove item from cart if it exists
        if item_id in cart:
            del cart[item_id]
            
        # Save cart to session
        request.session['cart'] = cart
        
        # Get updated cart data
        cart_data = get_cart_data(cart)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Item removed from cart',
            'cart_item_count': cart_data['item_count'],
            'cart_data': cart_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity < 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid quantity'
            }, status=400)
            
        cart = request.session.get('cart', {})
        
        if quantity == 0:
            if item_id in cart:
                del cart[item_id]
        else:
            cart[item_id] = quantity
            
        request.session['cart'] = cart
        
        # Get updated cart data
        cart_data = get_cart_data(cart)
        
        return JsonResponse({
            'status': 'success',
            'cart_item_count': cart_data['item_count'],
            'cart_data': cart_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def checkout(request):
    """Process the checkout and create an order"""
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty')
        return redirect('restaurant:menu')
    
    try:
        # Get or create a customer for the current user
        customer, created = Customer.objects.get_or_create(
            email=request.user.email,
            defaults={
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'phone': request.user.phone or ''
            }
        )
        
        # Get the first available table or create a default one if none exists
        table = Table.objects.filter(status='VACANT').first()
        if not table:
            table = Table.objects.create(
                number='ONLINE-1',
                capacity=4,
                status='VACANT',
                location='Online'
            )
        
        # Create the order
        order = Order.objects.create(
            customer=customer,
            table=table,
            created_by=request.user,
            status=Order.Status.PENDING
        )
        
        # Add items to the order
        items = MenuItem.objects.filter(id__in=cart.keys(), is_active=True)
        for item in items:
            quantity = cart.get(str(item.id), 0)
            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    item_name=item.name,
                    unit_price=item.price,
                    qty=quantity
                )
        
        # Calculate totals
        order.recalc_totals()
        
        # Clear the cart
        del request.session['cart']
        
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('restaurant:order_detail', order_id=order.id)
        
    except Exception as e:
        messages.error(request, f'Error processing your order: {str(e)}')
        return redirect('restaurant:menu')

@login_required
def order_history(request):
    """Display the user's order history"""
    from .models import Customer, Order, OrderItem
    
    try:
        customer = Customer.objects.get(email=request.user.email)
        orders = Order.objects.filter(customer=customer).select_related('table').prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('item'))
        ).order_by('-created_at')
        
        context = {
            'orders': orders,
            'active_tab': 'orders'
        }
        return render(request, 'restaurant/order_history.html', context)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found.')
        return redirect('restaurant:menu')

def register(request):
    if request.user.is_authenticated:
        return redirect('restaurant:dashboard')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('restaurant:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def debug_menu_items(request):
    """Temporary debug view to check menu items in the database"""
    # Get all categories
    categories = MenuCategory.objects.all()
    
    # Get all menu items with their categories
    menu_items = MenuItem.objects.select_related('category').all()
    
    # Get raw SQL data for debugging
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        category_data = []
        for table in tables:
            table_name = table[0]
            if table_name.startswith('restaurant_'):
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                category_data.append(f"{table_name}: {count} rows")
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
        'tables': category_data,
    }
    return render(request, 'restaurant/debug_menu.html', context)
