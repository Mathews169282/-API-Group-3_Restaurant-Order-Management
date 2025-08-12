from decimal import Decimal
from django.conf import settings
from django.db import models
from django import forms
from django.db.models import Q, Sum
from django.core.validators import MinValueValidator, MaxValueValidator



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MenuCategory(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class MenuItem(TimeStampedModel):
    category = models.ForeignKey(
        MenuCategory, related_name="items", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=40, unique=True, help_text="Internal code")
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("category", "name")]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Room(TimeStampedModel):
    class RoomType(models.TextChoices):
        SINGLE = "SINGLE", "Single"
        DOUBLE = "DOUBLE", "Double"
        SUITE = "SUITE", "Suite"

    number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField(null=True, blank=True)
    room_type = models.CharField(
        max_length=12, choices=RoomType.choices, default=RoomType.SINGLE
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["number"]
        indexes = [models.Index(fields=["number"])]

    def __str__(self):
        return f"Room {self.number}"


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer_name = models.CharField(max_length=100)
    room = models.ForeignKey(Room, related_name="orders", on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    notes = models.TextField(blank=True)

    
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Absolute discount, not percentage",
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="orders_created",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["customer_name"]),
        ]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name} ({self.room})"

    def recalc_totals(self, commit=True):
        """
        Recalculate subtotal (sum of line totals), apply discount and tax.
        Adjust logic if you want percentage tax/discount.
        """
        lines = self.items.all().values("qty", "unit_price")
        subtotal = sum((Decimal(l["qty"]) * Decimal(l["unit_price"])) for l in lines) or Decimal("0.00")

        
        total = subtotal - self.discount + self.tax
        if total < Decimal("0.00"):
            total = Decimal("0.00")

        self.subtotal = subtotal
        self.total = total

        if commit:
            self.save(update_fields=["subtotal", "total", "updated_at"])

    @property
    def amount_paid(self) -> Decimal:
        paid = self.payments.filter(status=Payment.Status.SUCCESS).aggregate(
            s=Sum("amount")
        )["s"] or Decimal("0.00")
        return paid

    @property
    def balance_due(self) -> Decimal:
        bal = (self.total or Decimal("0.00")) - self.amount_paid
        return bal if bal > 0 else Decimal("0.00")

    def is_editable(self) -> bool:
        return self.status in {Order.Status.PENDING, Order.Status.IN_PROGRESS}

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "room", "status", "notes", "discount", "tax"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_discount(self):
        val = self.cleaned_data.get("discount") or 0
        if val < 0:
            raise forms.ValidationError("Discount cannot be negative.")
        return val

    def clean_tax(self):
        val = self.cleaned_data.get("tax") or 0
        if val < 0:
            raise forms.ValidationError("Tax cannot be negative.")
        return val

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(
        MenuItem, related_name="order_items", null=True, blank=True, on_delete=models.SET_NULL
    )
    item_name = models.CharField(max_length=120)
    unit_price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    qty = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(check=Q(qty__gte=1), name="orderitem_qty_gte_1"),
            models.CheckConstraint(check=Q(unit_price__gte=0), name="orderitem_price_gte_0"),
        ]

    def __str__(self):
        return f"{self.item_name} × {self.qty}"

    @property
    def line_total(self) -> Decimal:
        return Decimal(self.qty) * (self.unit_price or Decimal("0.00"))

    def save(self, *args, **kwargs):
       
        if self.item and not self.item_name:
            self.item_name = self.item.name
        if self.item and (self.unit_price is None or self.unit_price == ""):
            self.unit_price = self.item.price
        super().save(*args, **kwargs)
        
        self.order.recalc_totals(commit=True)



class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        MPESA = "MPESA", "M-Pesa"  
        BANK = "BANK", "Bank Transfer"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.CASH)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    transaction_id = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"{self.method} {self.amount} ({self.status}) for Order #{self.order_id}"
