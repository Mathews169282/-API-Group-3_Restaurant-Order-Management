from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Adds sample menu categories and items to the database'

    def handle(self, *args, **options):
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
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            category_objs[cat.name] = cat
            self.stdout.write(self.style.SUCCESS(f'Created category: {cat.name}'))
        
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
            self.stdout.write(self.style.SUCCESS(f'Created menu item: {item.name} (${item.price})'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample menu data!'))
