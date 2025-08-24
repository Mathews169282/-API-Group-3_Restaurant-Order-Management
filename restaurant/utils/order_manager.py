"""
Advanced order management utilities for restaurant system
"""
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class OrderValidationError(Exception):
    """Custom exception for order validation errors"""
    pass


class OrderManager:
    """Advanced order management functionality"""
    
    @classmethod
    def get_status_transitions(cls):
        """Get valid status transitions"""
        return {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['PREPARING', 'CANCELLED'],
            'PREPARING': ['READY', 'CANCELLED'],
            'READY': ['SERVED', 'CANCELLED'],
            'SERVED': ['COMPLETED'],
            'COMPLETED': [],  # Final state
            'CANCELLED': [],  # Final state
        }
    
    @classmethod
    def create_order_with_validation(cls, customer, table_id, items_data, created_by, special_notes=""):
        """
        Create an order with comprehensive validation
        
        Args:
            customer: Customer instance or customer data
            table_id: Table ID
            items_data: List of dicts with 'item_id', 'quantity', 'special_instructions'
            created_by: User who is creating the order
            special_notes: General order notes
            
        Returns:
            Order instance
            
        Raises:
            OrderValidationError: If validation fails
        """
        from restaurant.models import Order, Table
        
        try:
            with transaction.atomic():
                # Validate and get table
                table = cls._validate_table(table_id)
                
                # Validate customer
                if isinstance(customer, dict):
                    customer = cls._get_or_create_customer(customer)
                
                # Validate items
                validated_items = cls._validate_order_items(items_data)
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    table=table,
                    notes=special_notes,
                    created_by=created_by,
                    status='PENDING'
                )
                
                # Add order items
                total_amount = cls._create_order_items(order, validated_items)
                
                # Update order totals
                order.recalc_totals()
                
                # Update table status
                table.status = 'OCCUPIED'
                table.save(update_fields=['status'])
                
                # Log order creation
                logger.info(f"Order {order.id} created by {created_by.email} for customer {customer.name}")
                
                return order
                
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}")
            raise OrderValidationError(f"Order creation failed: {str(e)}")
    
    @classmethod
    def _validate_table(cls, table_id):
        """Validate table availability"""
        from restaurant.models import Table
        try:
            table = Table.objects.select_for_update().get(id=table_id)
        except Table.DoesNotExist:
            raise OrderValidationError(f"Table with ID {table_id} does not exist")
        
        if table.status != 'VACANT':
            raise OrderValidationError(f"Table {table.number} is not available (Status: {table.get_status_display()})")
        
        return table
    
    @classmethod
    def _get_or_create_customer(cls, customer_data):
        """Get or create customer from data"""
        from restaurant.models import Customer
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in customer_data or not customer_data[field]:
                raise OrderValidationError(f"Customer {field} is required")
        
        # Try to get existing customer by email
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults={
                'name': customer_data['name'],
                'phone': customer_data.get('phone', ''),
                'address': customer_data.get('address', ''),
            }
        )
        
        if created:
            logger.info(f"New customer created: {customer.name} ({customer.email})")
        
        return customer
    
    @classmethod
    def _validate_order_items(cls, items_data):
        """Validate order items data"""
        from restaurant.models import MenuItem
        
        if not items_data:
            raise OrderValidationError("Order must contain at least one item")
        
        validated_items = []
        
        for item_data in items_data:
            # Validate required fields
            if 'item_id' not in item_data:
                raise OrderValidationError("Item ID is required for each order item")
            
            if 'quantity' not in item_data or item_data['quantity'] <= 0:
                raise OrderValidationError("Valid quantity is required for each order item")
            
            # Get and validate menu item
            try:
                menu_item = MenuItem.objects.get(id=item_data['item_id'], is_active=True)
            except MenuItem.DoesNotExist:
                raise OrderValidationError(f"Menu item with ID {item_data['item_id']} not found or inactive")
            
            validated_items.append({
                'menu_item': menu_item,
                'quantity': int(item_data['quantity']),
                'special_instructions': item_data.get('special_instructions', ''),
                'unit_price': menu_item.price
            })
        
        return validated_items
    
    @classmethod
    def _create_order_items(cls, order, validated_items):
        """Create order items and return total amount"""
        from restaurant.models import OrderItem
        
        total_amount = Decimal('0.00')
        
        for item_data in validated_items:
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            subtotal = unit_price * quantity
            
            OrderItem.objects.create(
                order=order,
                item=item_data['menu_item'],
                item_name=item_data['menu_item'].name,
                qty=quantity,
                unit_price=unit_price,
                notes=item_data['special_instructions']
            )
            
            total_amount += subtotal
        
        return total_amount
    
    @classmethod
    def update_order_status(cls, order_id, new_status, user=None, notes=""):
        """
        Update order status with validation and automatic actions
        
        Args:
            order_id: Order ID
            new_status: New status to set
            user: User performing the action
            notes: Additional notes for the status change
            
        Returns:
            Updated order instance
            
        Raises:
            OrderValidationError: If status transition is invalid
        """
        from restaurant.models import Order
        
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)
                old_status = order.status
                
                # Validate status transition
                transitions = cls.get_status_transitions()
                if new_status not in transitions.get(old_status, []):
                    raise OrderValidationError(
                        f"Invalid status transition from {old_status} to {new_status}"
                    )
                
                # Update order status
                order.status = new_status
                if notes:
                    order.notes = f"{order.notes}\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {notes}" if order.notes else notes
                
                # Set served_by if status is SERVED
                if new_status == 'SERVED' and user:
                    order.served_by = user
                
                order.save()
                
                # Handle automatic table management
                cls._handle_table_status_update(order, new_status)
                
                # Log status change
                user_info = f" by {user.email}" if user else ""
                logger.info(f"Order {order.id} status changed from {old_status} to {new_status}{user_info}")
                
                return order
                
        except Exception as e:
            if "Order matching query does not exist" in str(e):
                raise OrderValidationError("Order not found")
            logger.error(f"Failed to update order status: {str(e)}")
            raise OrderValidationError(f"Failed to update order status: {str(e)}")
    
    @classmethod
    def _handle_table_status_update(cls, order, new_status):
        """Handle automatic table status updates based on order status"""
        from restaurant.models import Order
        
        table = order.table
        
        # When order is completed or cancelled, check if table should be available
        if new_status in ['COMPLETED', 'CANCELLED']:
            # Check if table has any other active orders
            active_orders = Order.objects.filter(
                table=table,
                status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED']
            ).exclude(id=order.id)
            
            if not active_orders.exists():
                table.status = 'VACANT'
                table.save(update_fields=['status'])
                logger.info(f"Table {table.number} set to vacant")
    
    @classmethod
    def get_kitchen_queue(cls):
        """Get orders for kitchen display"""
        from restaurant.models import Order
        
        return Order.objects.filter(
            status__in=['CONFIRMED', 'PREPARING']
        ).select_related('customer', 'table', 'created_by').prefetch_related(
            'items__item__category'
        ).order_by('created_at')
    
    @classmethod
    def get_ready_orders(cls):
        """Get orders ready for serving"""
        from restaurant.models import Order
        
        return Order.objects.filter(status='READY').select_related(
            'customer', 'table'
        ).order_by('updated_at')
    
    @classmethod
    def get_pending_orders(cls):
        """Get pending orders that need confirmation"""
        from restaurant.models import Order
        
        return Order.objects.filter(status='PENDING').select_related(
            'customer', 'table', 'created_by'
        ).order_by('created_at')
    
    @classmethod
    def get_active_orders_by_table(cls, table_id):
        """Get active orders for a specific table"""
        from restaurant.models import Order
        
        return Order.objects.filter(
            table_id=table_id,
            status__in=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED']
        ).select_related('customer').prefetch_related('items__item')
    
    @classmethod
    def cancel_order(cls, order_id, user=None, reason=""):
        """Cancel an order with proper validation"""
        from restaurant.models import Order
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Only allow cancellation if order is not served or completed
            if order.status in ['SERVED', 'COMPLETED']:
                raise OrderValidationError("Cannot cancel an order that has been served or completed")
            
            notes = f"Cancelled: {reason}" if reason else "Cancelled"
            return cls.update_order_status(order_id, 'CANCELLED', user, notes)
            
        except Exception as e:
            if "Order matching query does not exist" in str(e):
                raise OrderValidationError("Order not found")
            raise OrderValidationError(str(e))
    
    @classmethod
    def get_order_summary(cls, order_id):
        """Get comprehensive order summary"""
        from restaurant.models import Order
        
        try:
            order = Order.objects.select_related(
                'customer', 'table', 'created_by', 'served_by'
            ).prefetch_related(
                'items__item__category'
            ).get(id=order_id)
            
            return {
                'order': order,
                'items': order.items.all(),
                'total_items': order.items.count(),
                'can_be_cancelled': order.status not in ['SERVED', 'COMPLETED', 'CANCELLED'],
                'valid_next_statuses': cls.get_status_transitions().get(order.status, [])
            }
            
        except Exception as e:
            if "Order matching query does not exist" in str(e):
                raise OrderValidationError("Order not found")
            raise OrderValidationError(str(e))


class KitchenManager:
    """Kitchen-specific order management"""
    
    @classmethod
    def get_kitchen_display_data(cls):
        """Get formatted data for kitchen display"""
        orders = OrderManager.get_kitchen_queue()
        
        kitchen_data = []
        for order in orders:
            items_by_category = {}
            
            for order_item in order.items.all():
                category = order_item.item.category.name if order_item.item else "Unknown"
                if category not in items_by_category:
                    items_by_category[category] = []
                
                items_by_category[category].append({
                    'name': order_item.item_name,
                    'quantity': order_item.qty,
                    'special_instructions': order_item.notes,
                })
            
            kitchen_data.append({
                'order_id': order.id,
                'order_number': f"#{order.id:06d}",
                'table_number': order.table.number,
                'customer_name': order.customer.name,
                'status': order.status,
                'created_at': order.created_at,
                'time_elapsed': timezone.now() - order.created_at,
                'items_by_category': items_by_category,
                'total_items': order.items.count(),
                'notes': order.notes
            })
        
        return kitchen_data
    
    @classmethod
    def mark_order_preparing(cls, order_id, user=None):
        """Mark order as preparing"""
        return OrderManager.update_order_status(
            order_id, 
            'PREPARING', 
            user, 
            "Kitchen started preparing"
        )
    
    @classmethod
    def mark_order_ready(cls, order_id, user=None):
        """Mark order as ready for serving"""
        return OrderManager.update_order_status(
            order_id, 
            'READY', 
            user, 
            "Order ready for pickup"
        )
