from decimal import Decimal
from django.conf import settings
from django.db import models
from django import forms
from django.db.models import Q, Sum
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, EmailValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that uses email as the unique identifier"""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email


class TimeStampedModel(models.Model):
    """
    Abstract base class with self-updating 'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MenuCategory(TimeStampedModel):
    """
    Model representing a category for menu items (e.g., Appetizers, Main Course, Desserts).
    """
    name = models.CharField(max_length=80, unique=True, help_text="Name of the category")
    is_active = models.BooleanField(default=True, help_text="Whether the category is currently available")

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(TimeStampedModel):
    """
    Model representing a menu item that can be ordered.
    """
    category = models.ForeignKey(
        MenuCategory, 
        related_name="items", 
        on_delete=models.PROTECT,
        help_text="Category this item belongs to"
    )
    name = models.CharField(max_length=120, help_text="Name of the menu item")
    sku = models.CharField(
        max_length=40, 
        unique=True, 
        help_text="Stock Keeping Unit - internal code for the item"
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Price in local currency"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this item is currently available"
    )
    description = models.TextField(blank=True, help_text="Optional description of the item")
    image = models.ImageField(
        upload_to='menu_items/',
        default='menu_items/default_food.jpg',
        help_text="Upload an image for this menu item"
    )

    class Meta:
        unique_together = [("category", "name")]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="restaurant_menuitem_name_idx"),
            models.Index(fields=["sku"], name="restaurant_menuitem_sku_idx"),
        ]
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Table(TimeStampedModel):
    """
    Model representing a restaurant table where orders are placed.
    """
    STATUS_CHOICES = [
        ('VACANT', 'Vacant'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
        ('CLEANING', 'Cleaning'),
    ]

    number = models.CharField(
        max_length=10, 
        unique=True,
        help_text="Table number or identifier"
    )
    capacity = models.PositiveSmallIntegerField(
        default=2,
        help_text="Maximum number of people that can be seated"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='VACANT',
        db_index=True,
        help_text="Current status of the table"
    )
    location = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Physical location in the restaurant (e.g., 'Patio', 'Main Room')"
    )

    class Meta:
        ordering = ['number']
        indexes = [
            models.Index(fields=['number'], name='restaurant_table_number_idx'),
            models.Index(fields=['status'], name='restaurant_table_status_idx'),
        ]

    def __str__(self):
        return f"Table {self.number} ({self.get_status_display()})"


class Order(TimeStampedModel):
    """
    Model representing a customer's order.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PREPARING = 'PREPARING', 'Preparing'
        READY = 'READY', 'Ready to Serve'
        SERVED = 'SERVED', 'Served'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey(
        'Customer',
        related_name='orders',
        on_delete=models.PROTECT,
        help_text="Customer who placed the order"
    )
    table = models.ForeignKey(
        Table,
        related_name='orders',
        on_delete=models.PROTECT,
        help_text="Table where the order was placed"
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING, 
        db_index=True,
        help_text="Current status of the order"
    )
    notes = models.TextField(
        blank=True,
        help_text="Special instructions or requests for the order"
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00"),
        help_text="Sum of all order items before discounts and taxes"
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Discount amount (absolute value, not percentage)"
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Tax amount"
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00"),
        help_text="Total amount after discounts and taxes"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="restaurant_orders_created",
        help_text="Staff member who created the order"
    )
    served_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="orders_served",
        on_delete=models.SET_NULL,
        help_text="Staff member who served the order"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='restaurant_order_status_idx'),
            models.Index(fields=['created_at'], name='resto_order_created_at_idx'),
        ]
        permissions = [
            ("can_manage_orders", "Can create, update, and delete orders"),
            ("can_view_reports", "Can view order reports and analytics"),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - {self.get_status_display()}"

    def recalc_totals(self, commit=True):
        """
        Recalculate subtotal (sum of line totals), apply discount and tax.
        """
        # Calculate subtotal from order items
        result = self.items.aggregate(
            subtotal=Sum(models.F('unit_price') * models.F('qty'), output_field=models.DecimalField())
        )
        self.subtotal = result['subtotal'] or Decimal('0.00')
        
        # Apply discount and tax
        self.total = self.subtotal - self.discount + self.tax
        
        if commit:
            self.save(update_fields=['subtotal', 'total'])
        return self.total

    @property
    def amount_paid(self):
        """Total amount paid for this order."""
        return self.payments.aggregate(
            total=Sum('amount', default=Decimal('0.00')
        ))['total']

    @property
    def balance_due(self):
        """Amount still to be paid."""
        return max(self.total - self.amount_paid, Decimal('0.00'))

    def is_editable(self):
        """Check if the order can be edited."""
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]


class OrderItem(TimeStampedModel):
    """
    Model representing an item within an order.
    """
    order = models.ForeignKey(
        Order, 
        related_name="items", 
        on_delete=models.CASCADE,
        help_text="Order this item belongs to"
    )
    item = models.ForeignKey(
        MenuItem, 
        related_name="order_items", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Menu item (null if item was deleted)"
    )
    item_name = models.CharField(
        max_length=120,
        help_text="Name of the item at the time of ordering"
    )
    unit_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Price per unit at the time of ordering"
    )
    qty = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity ordered"
    )
    notes = models.TextField(
        blank=True,
        help_text="Special instructions for this item"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.qty}x {self.item_name} (Order #{self.order_id})"

    @property
    def line_total(self):
        """Calculate the total for this line item."""
        return self.unit_price * self.qty

    def save(self, *args, **kwargs):
        """Save the order item and update the order totals."""
        # Set item name from menu item if not set and item exists
        if self.item and not self.item_name:
            self.item_name = self.item.name
        
        # Set unit price from menu item if not set and item exists
        if self.item and not self.unit_price:
            self.unit_price = self.item.price
        
        super().save(*args, **kwargs)
        self.order.recalc_totals()


class Payment(TimeStampedModel):
    """
    Model representing a payment for an order.
    """
    class Method(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Credit/Debit Card'
        MOBILE = 'MOBILE', 'Mobile Payment'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    order = models.ForeignKey(
        Order, 
        related_name="payments", 
        on_delete=models.CASCADE,
        help_text="Order this payment is for"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Payment amount"
    )
    method = models.CharField(
        max_length=10, 
        choices=Method.choices, 
        default=Method.CASH,
        help_text="Payment method used"
    )
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.COMPLETED,
        help_text="Payment status"
    )
    transaction_id = models.CharField(
        max_length=120, 
        blank=True,
        help_text="Transaction ID or reference number from payment processor"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional payment details or notes"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Staff member who processed the payment"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.get_method_display()} Payment of ${self.amount} for Order #{self.order_id}"

    def save(self, *args, **kwargs):
        """Save the payment and update the order status if fully paid."""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # If this is a new payment and it's completed, check if order is fully paid
        if is_new and self.status == self.Status.COMPLETED:
            if self.order.balance_due <= 0:
                self.order.status = Order.Status.COMPLETED
                self.order.save(update_fields=['status', 'updated_at'])


class Customer(models.Model):
    """
    Model representing a restaurant customer.
    """
    name = models.CharField(
        max_length=100,
        help_text="Enter the customer's full name",
        validators=[MinLengthValidator(2, "Name must be at least 2 characters long")]
    )
    
    phone = models.CharField(
        max_length=15,
        help_text="Enter customer's phone number",
        validators=[MinLengthValidator(10, "Phone number must be at least 10 digits")]
    )
    
    email = models.EmailField(
        max_length=100,
        unique=True,
        help_text="Enter customer's email address",
        validators=[EmailValidator(message="Enter a valid email address")]
    )
    
    address = models.TextField(
        blank=True,
        help_text="Customer's address (for delivery or billing)"
    )
    
    loyalty_points = models.PositiveIntegerField(
        default=0,
        help_text="Customer's loyalty points"
    )
    
    is_vip = models.BooleanField(
        default=False,
        help_text="Designates whether the customer is a VIP"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the customer"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [
            models.Index(fields=['name'], name='restaurant_customer_name_idx'),
            models.Index(fields=['email'], name='restaurant_customer_email_idx'),
            models.Index(fields=['phone'], name='restaurant_customer_phone_idx'),
            models.Index(fields=['is_vip'], name='restaurant_customer_vip_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def total_spent(self):
        """Calculate total amount spent by the customer."""
        return Order.objects.filter(
            customer=self, 
            status=Order.Status.COMPLETED
        ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
