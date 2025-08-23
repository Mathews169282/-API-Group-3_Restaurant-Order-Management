from decimal import Decimal
from typing import List, Dict

from rest_framework import serializers
from .models import (
    MenuCategory, MenuItem, Table, Order, OrderItem, Payment, Customer
)


class MenuCategorySerializer(serializers.ModelSerializer):
    """Serializer for the MenuCategory model."""
    class Meta:
        model = MenuCategory
        fields = ("id", "name", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for the MenuItem model with category name included."""
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = ("id", "name", "sku", "price", "is_active", "description", 
                 "category", "category_name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TableSerializer(serializers.ModelSerializer):
    """Serializer for the Table model."""
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Table
        fields = ("id", "number", "capacity", "status", "status_display", 
                 "location", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for the Customer model."""
    total_spent = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, 
        help_text="Total amount spent by the customer"
    )
    
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "address", 
                 "loyalty_points", "is_vip", "total_spent", "notes", 
                 "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at", "total_spent")


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""
    method_display = serializers.CharField(
        source="get_method_display", 
        read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", 
        read_only=True
    )
    processed_by_username = serializers.CharField(
        source="processed_by.username", 
        read_only=True
    )

    class Meta:
        model = Payment
        fields = ("id", "order", "amount", "method", "method_display", 
                 "status", "status_display", "transaction_id", "notes",
                 "processed_by", "processed_by_username", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for the OrderItem model with line total calculation."""
    id = serializers.IntegerField(required=False)
    line_total = serializers.SerializerMethodField(read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False
    )

    class Meta:
        model = OrderItem
        fields = ("id", "order", "item", "item_name", "unit_price", 
                 "qty", "notes", "line_total", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def get_line_total(self, obj):
        return obj.line_total


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model with nested items and payments."""
    items = OrderItemSerializer(many=True, required=False)
    payments = PaymentSerializer(many=True, read_only=True)
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())
    table_number = serializers.CharField(source="table.number", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", 
        read_only=True
    )
    amount_paid = serializers.SerializerMethodField(read_only=True)
    balance_due = serializers.SerializerMethodField(read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", 
        read_only=True
    )
    served_by_username = serializers.CharField(
        source="served_by.username", 
        read_only=True
    )
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Order
        fields = (
            "id", "customer", "customer_name", "table", "table_number", "status", 
            "status_display", "notes", "items", "payments", "subtotal", "discount", 
            "tax", "total", "amount_paid", "balance_due", "created_by", 
            "created_by_username", "served_by", "served_by_username", 
            "created_at", "updated_at"
        )
        read_only_fields = (
            "id", "created_at", "updated_at", "subtotal", "total", 
            "amount_paid", "balance_due"
        )

    def get_amount_paid(self, obj):
        return obj.amount_paid

    def get_balance_due(self, obj):
        return obj.balance_due

    def _sync_items(self, order: Order, items_data: List[Dict]):
        """
        Sync order items with the provided data.
        - If an item dict has 'id', update that row
        - Else create a new row
        - Delete rows that were not sent
        """
        if items_data is None:
            return

        # Get all item IDs from the request data
        item_ids = [item.get('id') for item in items_data if item.get('id')]
        
        # Delete items not included in the request
        OrderItem.objects.filter(order=order).exclude(id__in=item_ids).delete()
        
        # Create or update items
        for item_data in items_data:
            item_id = item_data.pop('id', None)
            if item_id:
                # Update existing item
                OrderItem.objects.filter(id=item_id, order=order).update(**item_data)
            else:
                # Create new item
                OrderItem.objects.create(order=order, **item_data)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        self._sync_items(order, items_data)
        order.recalc_totals()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update items if provided
        if items_data is not None:
            self._sync_items(instance, items_data)
        
        instance.recalc_totals()
        instance.save()
        return instance
