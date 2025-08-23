import os
import django
import sys

# Set up Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from restaurant.models import MenuCategory, MenuItem
import uuid

def add_menu_items():
    # Create or get categories
    categories = {}
    for name in ['Appetizers', 'Main Courses', 'Desserts']:
        category, created = MenuCategory.objects.get_or_create(
            name=name,
            defaults={'is_active': True}
        )
        categories[name] = category
        print(f"Category: {name} - {'Created' if created else 'Exists'}")

    # Menu items with corresponding image filenames
    menu_items = [
        {
            'name': 'Garlic Bread',
            'price': 5.99,
            'category': 'Appetizers',
            'description': 'Toasted with garlic butter',
            'image': 'garlicbread.jpg'
        },
        {
            'name': 'Bruschetta',
            'price': 7.99,
            'category': 'Appetizers',
            'description': 'Toasted bread with tomatoes',
            'image': 'bruschetta.jpg'
        },
        {
            'name': 'Grilled Salmon',
            'price': 24.99,
            'category': 'Main Courses',
            'description': 'With lemon butter sauce',
            'image': 'grilledsalmon.jpg'
        },
        {
            'name': 'Pasta Carbonara',
            'price': 18.99,
            'category': 'Main Courses',
            'description': 'Classic Italian pasta',
            'image': 'pastacarbonara.jpg'
        },
        {
            'name': 'Chocolate Lava Cake',
            'price': 8.99,
            'category': 'Desserts',
            'description': 'Warm with molten center',
            'image': 'chocolatelavacake.jpg'
        }
    ]

    # Add menu items
    for item_data in menu_items:
        name = item_data['name']
        if not MenuItem.objects.filter(name=name).exists():
            # Create a simple SKU
            sku = f"{name.replace(' ', '').upper()[:6]}-{str(uuid.uuid4())[:4]}"
            
            # Create the menu item
            menu_item = MenuItem(
                name=name,
                sku=sku,
                price=item_data['price'],
                description=item_data['description'],
                category=categories[item_data['category']],
                is_active=True
            )
            
            # Set the image if it exists
            image_path = os.path.join('menu_items', item_data['image'].lower())
            full_image_path = os.path.join('media', 'menu_items', item_data['image'].lower())
            
            if os.path.exists(full_image_path):
                menu_item.image = image_path
                print(f"Added image for {name}")
            else:
                print(f"Image not found for {name}: {full_image_path}")
            
            menu_item.save()
            print(f"Added menu item: {name}")
        else:
            print(f"Menu item already exists: {name}")

    print("\nMenu population completed!")

if __name__ == "__main__":
    add_menu_items()
