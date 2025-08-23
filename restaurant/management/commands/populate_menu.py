from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem
import uuid

class Command(BaseCommand):
    help = 'Populates the database with sample menu items and categories'

    def handle(self, *args, **options):
        # Create or get categories
        categories = {}
        for name in ['Appetizers', 'Main Courses', 'Desserts']:
            category, created = MenuCategory.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            categories[name] = category
            self.stdout.write(self.style.SUCCESS(f'Category: {name} - {"Created" if created else "Exists"}'))

        # Menu items data
        menu_items = [
            {'name': 'Garlic Bread', 'price': 5.99, 'category': 'Appetizers', 'description': 'Toasted with garlic butter'},
            {'name': 'Bruschetta', 'price': 7.99, 'category': 'Appetizers', 'description': 'Toasted bread with tomatoes'},
            {'name': 'Grilled Salmon', 'price': 24.99, 'category': 'Main Courses', 'description': 'With lemon butter sauce'},
            {'name': 'Pasta Carbonara', 'price': 18.99, 'category': 'Main Courses', 'description': 'Classic Italian pasta'},
            {'name': 'Chocolate Lava Cake', 'price': 8.99, 'category': 'Desserts', 'description': 'Warm with molten center'}
        ]

        # Add menu items
        for item_data in menu_items:
            name = item_data['name']
            if not MenuItem.objects.filter(name=name).exists():
                MenuItem.objects.create(
                    name=name,
                    sku=f"{name.replace(' ', '').upper()[:6]}-{str(uuid.uuid4())[:4]}",
                    price=item_data['price'],
                    description=item_data['description'],
                    category=categories[item_data['category']],
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Added menu item: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Menu item already exists: {name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated menu data!'))
