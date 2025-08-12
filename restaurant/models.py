from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator

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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.name} ({self.email})"
