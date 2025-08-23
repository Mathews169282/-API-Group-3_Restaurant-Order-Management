@echo off
echo Resetting database and setting up sample data...

REM Remove existing database if it exists
if exist db.sqlite3 (
    echo Removing existing database...
    del db.sqlite3
)

echo Creating new database and applying migrations...
python manage.py migrate

echo Creating superuser...
python manage.py createsuperuser --username=admin --email=admin@example.com --noinput

echo Adding sample data...
python -c "
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

# Import models
from restaurant.models import MenuCategory, MenuItem

# Create categories
categories = [
    {'name': 'Appetizers', 'description': 'Delicious starters to begin your meal'},
    {'name': 'Main Courses', 'description': 'Hearty and satisfying main dishes'},
    {'name': 'Desserts', 'description': 'Sweet treats to end your meal'}
]

menu_items = [
    {'category': 'Appetizers', 'name': 'Garlic Bread', 'description': 'Toasted bread with garlic butter', 'price': 5.99},
    {'category': 'Appetizers', 'name': 'Bruschetta', 'description': 'Toasted bread with tomatoes and basil', 'price': 7.99},
    {'category': 'Main Courses', 'name': 'Grilled Salmon', 'description': 'Fresh salmon with lemon butter sauce', 'price': 24.99},
    {'category': 'Main Courses', 'name': 'Pasta Carbonara', 'description': 'Creamy pasta with bacon and parmesan', 'price': 18.99},
    {'category': 'Desserts', 'name': 'Chocolate Lava Cake', 'description': 'Warm chocolate cake with a molten center', 'price': 8.99},
    {'category': 'Desserts', 'name': 'New York Cheesecake', 'description': 'Classic cheesecake with strawberry topping', 'price': 7.99}
]

# Add categories
category_objs = {}
for cat_data in categories:
    cat, created = MenuCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description'], 'is_active': True}
    )
    category_objs[cat.name] = cat
    print(f"Created category: {cat.name}")

# Add menu items
for item_data in menu_items:
    category = category_objs[item_data['category']]
    item, created = MenuItem.objects.get_or_create(
        name=item_data['name'],
        category=category,
        defaults={
            'description': item_data['description'],
            'price': item_data['price'],
            'is_active': True
        }
    )
    print(f"Created menu item: {item.name} (${item.price})")
"

echo Setup complete!
pause
