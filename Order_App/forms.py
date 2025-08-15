
from django import forms
from .models import Order, Room

class OrderForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_active=True).order_by("number")
    )

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