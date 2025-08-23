import os
import django
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from restaurant.models import MenuCategory, MenuItem

def add_menu_items():
    # Create categories if they don't exist
    categories = {}
    for name in ['Appetizers', 'Main Courses', 'Desserts']:
        cat, created = MenuCategory.objects.get_or_create(
            name=name,
            defaults={'is_active': True}
        )
        categories[name] = cat
        print(f"Category: {name} - {'Created' if created else 'Exists'}")

    # Menu items to add
    menu_items = [
        {'name': 'Garlic Bread', 'category': 'Appetizers', 'price': 5.99, 'desc': 'Toasted with garlic butter'},
        {'name': 'Bruschetta', 'category': 'Appetizers', 'price': 7.99, 'desc': 'Toasted bread with tomatoes'},
        {'name': 'Grilled Salmon', 'category': 'Main Courses', 'price': 24.99, 'desc': 'With lemon butter sauce'},
        {'name': 'Pasta Carbonara', 'category': 'Main Courses', 'price': 18.99, 'desc': 'Classic Italian pasta'},
        {'name': 'Chocolate Lava Cake', 'category': 'Desserts', 'price': 8.99, 'desc': 'Warm with molten center'}
    ]

    # Add menu items
    for item in menu_items:
        if not MenuItem.objects.filter(name=item['name']).exists():
            MenuItem.objects.create(
                name=item['name'],
                sku=f"{item['name'].replace(' ', '').upper()[:6]}-{str(uuid.uuid4())[:4]}",
                description=item['desc'],
                price=item['price'],
                category=categories[item['category']],
                is_active=True
            )
            print(f"Added: {item['name']}")
        else:
            print(f"Skipped (already exists): {item['name']}")

    # Print summary
    print("\n=== Menu Summary ===")
    for cat in categories.values():
        count = MenuItem.objects.filter(category=cat).count()
        print(f"{cat.name}: {count} items")
    print(f"Total items: {MenuItem.objects.count()}")

if __name__ == "__main__":
    add_menu_items()
