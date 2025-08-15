
from decimal import Decimal
from typing import List, Dict

from rest_framework import serializers
from .models import (
    MenuCategory, MenuItem,
    Room, Order, OrderItem, Payment
)


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ("id", "name", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class MenuItemSerializer(serializers.ModelSerializer):
    dietary_info = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id',
            'category',
            'name',
            'sku',
            'description',
            'price',
            'image',
            'image_url',
            'preparation_time',
            'is_active',
            'in_stock',
            'inventory_count',
            'low_stock_threshold',
            'is_vegetarian',
            'is_vegan',
            'is_gluten_free',
            'has_nuts',
            'dietary_info',
            'availability_status',
            'created',
            'modified'
        ]
        read_only_fields = [
            'id',
            'created',
            'modified',
            'dietary_info',
            'availability_status',
            'image_url'
        ]
        extra_kwargs = {
            'image': {'write_only': True},
            'price': {'min_value': 0},
            'inventory_count': {'min_value': 0},
            'low_stock_threshold': {'min_value': 0},
            'preparation_time': {'min_value': 0}
        }

    def get_dietary_info(self, obj):
        return obj.get_dietary_info()

    def get_availability_status(self, obj):
        return obj.availability_status()

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def validate(self, data):
        if data.get('inventory_count', 0) > 0 and not data.get('in_stock', True):
            raise serializers.ValidationError(
                "Inventory count must be 0 when item is marked out of stock"
            )
        if data.get('is_vegan') and not data.get('is_vegetarian'):
            raise serializers.ValidationError(
                "Vegan items must also be vegetarian"
            )
        return data
    
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "number", "floor", "room_type", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "order", "amount", "method", "status", "transaction_id", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")



class OrderItemSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(required=False)
    line_total = serializers.SerializerMethodField(read_only=True)

   
    item_name_resolved = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "item", "item_name", "unit_price", "qty", "line_total", "item_name_resolved", "created_at", "updated_at")
        read_only_fields = ("line_total", "created_at", "updated_at")

    def get_line_total(self, obj):
        return str(Decimal(obj.qty) * Decimal(obj.unit_price))


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)

    
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    room_number = serializers.CharField(source="room.number", read_only=True)

    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount_paid = serializers.SerializerMethodField(read_only=True)
    balance_due = serializers.SerializerMethodField(read_only=True)

    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_name",
            "room", "room_number",
            "status",
            "notes",
            "subtotal", "discount", "tax", "total",
            "amount_paid", "balance_due",
            "items", "payments",
            "created_by", "created_by_username",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "subtotal", "total", "amount_paid", "balance_due", "created_at", "updated_at")

    
    def get_amount_paid(self, obj):
        return str(obj.amount_paid)

    def get_balance_due(self, obj):
        return str(obj.balance_due)

   
    def _sync_items(self, order: Order, items_data: List[Dict]):
        """
        Upsert strategy for nested items:
        - if an item dict has 'id', update that row
        - else create a new row
        - delete rows that were not sent
        """
        existing = {oi.id: oi for oi in order.items.all()}
        seen_ids = set()

        for item in items_data:
            oi_id = item.get("id")

           
            menu_item = item.get("item", None)
            if menu_item and not item.get("item_name"):
               
                pass

            if oi_id and oi_id in existing:
                oi = existing[oi_id]
                for attr in ("item", "item_name", "unit_price", "qty"):
                    if attr in item:
                        setattr(oi, attr, item[attr])
                oi.save()
                seen_ids.add(oi_id)
            else:
                OrderItem.objects.create(order=order, **item)

        
        to_delete = [oi for oid, oi in existing.items() if oid not in seen_ids]
        if to_delete:
            OrderItem.objects.filter(id__in=[x.id for x in to_delete]).delete()

        
        order.recalc_totals(commit=True)

    
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        
        order = Order.objects.create(**validated_data)
       
        OrderItem.objects.bulk_create([OrderItem(order=order, **item) for item in items_data])
        order.recalc_totals(commit=True)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            self._sync_items(instance, items_data)
        else:
            
            instance.recalc_totals(commit=True)

        return instance