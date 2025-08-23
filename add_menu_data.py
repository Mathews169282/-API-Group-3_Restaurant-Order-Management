import os
import django

def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
    django.setup()
    
    from restaurant.models import MenuCategory, MenuItem
    
    # Create categories
    categories = [
        {"name": "Appetizers", "description": "Delicious starters"},
        {"name": "Main Courses", "description": "Hearty main dishes"},
        {"name": "Desserts", "description": "Sweet treats"},
    ]
    
    for cat_data in categories:
        MenuCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"], "is_active": True}
        )
    
    # Get or create menu items
    menu_items = [
        {"name": "Garlic Bread", "category": "Appetizers", "price": 5.99, "description": "Toasted bread with garlic butter"},
        {"name": "Bruschetta", "category": "Appetizers", "price": 7.99, "description": "Toasted bread with tomatoes and basil"},
        {"name": "Steak", "category": "Main Courses", "price": 24.99, "description": "Grilled sirloin with vegetables"},
        {"name": "Pasta Carbonara", "category": "Main Courses", "price": 16.99, "description": "Creamy pasta with bacon and parmesan"},
        {"name": "Chocolate Cake", "category": "Desserts", "price": 8.99, "description": "Rich chocolate cake with ice cream"},
        {"name": "Cheesecake", "category": "Desserts", "price": 7.99, "description": "New York style cheesecake with berry sauce"},
    ]
    
    for item_data in menu_items:
        category = MenuCategory.objects.get(name=item_data["category"])
        MenuItem.objects.get_or_create(
            name=item_data["name"],
            category=category,
            defaults={
                "price": item_data["price"],
                "description": item_data["description"],
                "is_active": True,
                "sku": f"{category.name[:3].upper()}-{item_data['name'][:3].upper()}-001"
            }
        )
    
    print("Successfully added sample menu data!")

if __name__ == "__main__":
    run()
