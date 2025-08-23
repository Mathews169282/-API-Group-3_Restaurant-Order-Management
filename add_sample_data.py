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

def add_sample_data():
    """Add sample menu categories and items"""
    from restaurant.models import MenuCategory, MenuItem
    
    print("Adding sample menu data...")
    
    # Create categories
    categories = [
        {
            'name': 'Appetizers',
            'description': 'Delicious starters to begin your meal',
            'is_active': True
        },
        {
            'name': 'Main Courses',
            'description': 'Hearty and satisfying main dishes',
            'is_active': True
        },
        {
            'name': 'Desserts',
            'description': 'Sweet treats to end your meal',
            'is_active': True
        }
    ]
    
    menu_items = [
        {
            'category_name': 'Appetizers',
            'name': 'Garlic Bread',
            'description': 'Toasted bread with garlic butter',
            'price': 5.99,
            'is_active': True
        },
        {
            'category_name': 'Appetizers',
            'name': 'Bruschetta',
            'description': 'Toasted bread topped with tomatoes, garlic, and fresh basil',
            'price': 7.99,
            'is_active': True
        },
        {
            'category_name': 'Main Courses',
            'name': 'Grilled Salmon',
            'description': 'Fresh salmon fillet with lemon butter sauce',
            'price': 24.99,
            'is_active': True
        },
        {
            'category_name': 'Main Courses',
            'name': 'Pasta Carbonara',
            'description': 'Creamy pasta with bacon and parmesan',
            'price': 18.99,
            'is_active': True
        },
        {
            'category_name': 'Desserts',
            'name': 'Chocolate Lava Cake',
            'description': 'Warm chocolate cake with a molten center',
            'price': 8.99,
            'is_active': True
        },
        {
            'category_name': 'Desserts',
            'name': 'New York Cheesecake',
            'description': 'Classic cheesecake with strawberry topping',
            'price': 7.99,
            'is_active': True
        }
    ]
    
    # Add categories
    category_objs = {}
    for cat_data in categories:
        cat, created = MenuCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'is_active': cat_data['is_active']
            }
        )
        category_objs[cat.name] = cat
        print(f"{'Created' if created else 'Updated'} category: {cat.name}")
    
    # Add menu items
    for item_data in menu_items:
        category = category_objs.get(item_data['category_name'])
        if not category:
            print(f"Category not found: {item_data['category_name']}")
            continue
            
        item, created = MenuItem.objects.get_or_create(
            name=item_data['name'],
            category=category,
            defaults={
                'description': item_data['description'],
                'price': item_data['price'],
                'is_active': item_data['is_active']
            }
        )
        print(f"{'Created' if created else 'Updated'} menu item: {item.name} (${item.price})")
    
    print("\nSample data added successfully!")

if __name__ == "__main__":
    setup_django()
    add_sample_data()
