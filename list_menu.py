import os
import django

def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
    django.setup()
    
    from restaurant.models import MenuCategory, MenuItem
    
    print("=== Menu Categories ===")
    for cat in MenuCategory.objects.all():
        print(f"- {cat.name} (ID: {cat.id}, Active: {cat.is_active})")
    
    print("\n=== Menu Items ===")
    for item in MenuItem.objects.all():
        print(f"- {item.name} (ID: {item.id}, Category: {item.category.name if item.category else 'None'}, Active: {item.is_active})")

if __name__ == "__main__":
    run()
