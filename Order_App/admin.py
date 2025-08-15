#from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import MenuCategory, MenuItem, Room, Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "room", "status", "subtotal", "discount", "tax", "total", "created_at")
    list_filter = ("status", "room")
    search_fields = ("customer_name", "room__number")
    inlines = [OrderItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")

admin.site.register(MenuCategory)
admin.site.register(Room)
admin.site.register(Payment)
