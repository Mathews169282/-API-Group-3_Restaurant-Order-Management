"""
Enhanced order management views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from restaurant.models import Order, Table, Customer, MenuItem, MenuCategory
from restaurant.utils.order_manager import OrderManager, KitchenManager, OrderValidationError

logger = logging.getLogger(__name__)


@login_required
def create_order_view(request):
    """Enhanced order creation view"""
    if request.method == 'GET':
        # Get available tables and menu items
        available_tables = Table.objects.filter(status='VACANT')
        categories = MenuCategory.objects.filter(is_active=True).prefetch_related('items')
        
        context = {
            'available_tables': available_tables,
            'categories': categories,
        }
        return render(request, 'restaurant/create_order.html', context)
    
    elif request.method == 'POST':
        try:
            # Parse order data
            table_id = request.POST.get('table_id')
            customer_data = {
                'name': request.POST.get('customer_name'),
                'email': request.POST.get('customer_email'),
                'phone': request.POST.get('customer_phone', ''),
            }
            special_notes = request.POST.get('special_notes', '')
            
            # Parse order items from form data
            items_data = []
            item_count = int(request.POST.get('item_count', 0))
            for i in range(item_count):
                item_id = request.POST.get(f'item_{i}_id')
                quantity = request.POST.get(f'item_{i}_quantity')
                special_instructions = request.POST.get(f'item_{i}_instructions', '')
                
                if item_id and quantity:
                    items_data.append({
                        'item_id': int(item_id),
                        'quantity': int(quantity),
                        'special_instructions': special_instructions
                    })
            
            if not items_data:
                messages.error(request, "Please add at least one item to the order.")
                return redirect('restaurant:create_order')
            
            # Create order using OrderManager
            order = OrderManager.create_order_with_validation(
                customer=customer_data,
                table_id=int(table_id),
                items_data=items_data,
                created_by=request.user,
                special_notes=special_notes
            )
            
            messages.success(request, f'Order #{order.id:06d} created successfully!')
            return redirect('restaurant:order_detail', order_id=order.id)
            
        except OrderValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            messages.error(request, "Failed to create order. Please try again.")
        
        # Return to form with errors
        available_tables = Table.objects.filter(status='VACANT')
        categories = MenuCategory.objects.filter(is_active=True).prefetch_related('items')
        
        context = {
            'available_tables': available_tables,
            'categories': categories,
        }
        return render(request, 'restaurant/create_order.html', context)


@login_required
def order_detail_view(request, order_id):
    """Enhanced order detail view"""
    try:
        order_summary = OrderManager.get_order_summary(order_id)
        context = {
            'order': order_summary['order'],
            'items': order_summary['items'],
            'total_items': order_summary['total_items'],
            'can_be_cancelled': order_summary['can_be_cancelled'],
            'valid_next_statuses': order_summary['valid_next_statuses'],
            'status_transitions': OrderManager.get_status_transitions(),
        }
        return render(request, 'restaurant/order_detail.html', context)
    except OrderValidationError as e:
        messages.error(request, str(e))
        return redirect('restaurant:dashboard')


@login_required
@require_POST
def update_order_status_view(request, order_id):
    """Update order status"""
    try:
        new_status = request.POST.get('new_status')
        notes = request.POST.get('notes', '')
        
        if not new_status:
            raise OrderValidationError("New status is required")
        
        order = OrderManager.update_order_status(order_id, new_status, request.user, notes)
        messages.success(request, f'Order status updated to {order.get_status_display()}')
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_status_display()}',
                'new_status': new_status
            })
        
        return redirect('restaurant:order_detail', order_id=order_id)
        
    except OrderValidationError as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, str(e))
        return redirect('restaurant:order_detail', order_id=order_id)


@login_required
@require_POST
def cancel_order_view(request, order_id):
    """Cancel an order"""
    try:
        reason = request.POST.get('reason', '')
        order = OrderManager.cancel_order(order_id, request.user, reason)
        messages.success(request, f'Order #{order.id:06d} has been cancelled')
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': f'Order #{order.id:06d} has been cancelled'
            })
        
        return redirect('restaurant:order_detail', order_id=order_id)
        
    except OrderValidationError as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, str(e))
        return redirect('restaurant:order_detail', order_id=order_id)


@login_required
def kitchen_queue_view(request):
    """Kitchen queue display"""
    kitchen_data = KitchenManager.get_kitchen_display_data()
    
    context = {
        'kitchen_orders': kitchen_data,
        'page_title': 'Kitchen Queue'
    }
    return render(request, 'restaurant/kitchen_queue.html', context)


@login_required
@require_POST
def mark_order_preparing(request, order_id):
    """Mark order as preparing (AJAX endpoint)"""
    try:
        order = KitchenManager.mark_order_preparing(order_id, request.user)
        return JsonResponse({
            'success': True,
            'message': f'Order #{order.id:06d} marked as preparing',
            'new_status': 'PREPARING'
        })
    except OrderValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def mark_order_ready(request, order_id):
    """Mark order as ready (AJAX endpoint)"""
    try:
        order = KitchenManager.mark_order_ready(order_id, request.user)
        return JsonResponse({
            'success': True,
            'message': f'Order #{order.id:06d} is ready for serving',
            'new_status': 'READY'
        })
    except OrderValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def ready_orders_view(request):
    """View orders ready for serving"""
    ready_orders = OrderManager.get_ready_orders()
    
    context = {
        'orders': ready_orders,
        'page_title': 'Ready Orders'
    }
    return render(request, 'restaurant/ready_orders.html', context)


@login_required
def pending_orders_view(request):
    """View pending orders that need confirmation"""
    pending_orders = OrderManager.get_pending_orders()
    
    context = {
        'orders': pending_orders,
        'page_title': 'Pending Orders'
    }
    return render(request, 'restaurant/pending_orders.html', context)


@login_required
def table_orders_view(request, table_id):
    """View active orders for a specific table"""
    table = get_object_or_404(Table, id=table_id)
    active_orders = OrderManager.get_active_orders_by_table(table_id)
    
    context = {
        'table': table,
        'orders': active_orders,
        'page_title': f'Table {table.number} Orders'
    }
    return render(request, 'restaurant/table_orders.html', context)


# API Endpoints for AJAX requests
@login_required
@require_http_methods(["GET"])
def api_kitchen_queue(request):
    """API endpoint for kitchen queue data"""
    try:
        kitchen_data = KitchenManager.get_kitchen_display_data()
        return JsonResponse({
            'success': True,
            'data': kitchen_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def api_order_status(request, order_id):
    """API endpoint to get order status"""
    try:
        order = get_object_or_404(Order, id=order_id)
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'status_display': order.get_status_display(),
            'valid_transitions': OrderManager.get_status_transitions().get(order.status, [])
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def api_table_status(request, table_id):
    """API endpoint to get table status and active orders"""
    try:
        table = get_object_or_404(Table, id=table_id)
        active_orders = OrderManager.get_active_orders_by_table(table_id)
        
        orders_data = []
        for order in active_orders:
            orders_data.append({
                'id': order.id,
                'customer_name': order.customer.name,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total': str(order.total),
                'created_at': order.created_at.isoformat(),
                'items_count': order.items.count()
            })
        
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'number': table.number,
                'status': table.status,
                'status_display': table.get_status_display(),
                'capacity': table.capacity,
                'location': table.location
            },
            'active_orders': orders_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
