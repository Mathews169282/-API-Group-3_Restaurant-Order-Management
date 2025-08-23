import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
    django.setup()

def list_menu():
    """List all menu categories and items"""
    from restaurant.models import MenuCategory, MenuItem
    
    print("=== Menu Categories ===")
    categories = MenuCategory.objects.all()
    
    if not categories:
        print("No categories found.")
        return
    
    for category in categories:
        print(f"\n{category.name} (ID: {category.id}, Active: {category.is_active})")
        print(f"Description: {category.description}")
        
        items = MenuItem.objects.filter(category=category, is_active=True)
        if items:
            print("\n  Menu Items:")
            for item in items:
                print(f"  - {item.name} (ID: {item.id}, Price: ${item.price})")
                print(f"    Description: {item.description}")
                if hasattr(item, 'image') and item.image:
                    print(f"    Image: {item.image}")
        else:
            print("  No active items in this category.")

if __name__ == "__main__":
    setup_django()
    list_menu()
