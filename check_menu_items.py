import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from restaurant.models import MenuCategory, MenuItem

print("=== Menu Categories ===")
for category in MenuCategory.objects.all():
    print(f"- {category.name} (Active: {category.is_active})")

print("\n=== Menu Items ===")
for item in MenuItem.objects.select_related('category').all():
    print(f"- {item.name} (Category: {item.category.name}, Price: ${item.price})")

print("\n=== Summary ===")
print(f"Total categories: {MenuCategory.objects.count()}")
print(f"Total menu items: {MenuItem.objects.count()}")
