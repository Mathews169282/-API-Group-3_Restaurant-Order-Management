from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem
import uuid

class Command(BaseCommand):
    help = 'Add sample menu items to the database'

    def handle(self, *args, **options):
        # Get or create categories
        categories = {
            'Appetizers': MenuCategory.objects.get_or_create(
                name='Appetizers', 
                defaults={'is_active': True}
            )[0],
            'Main Courses': MenuCategory.objects.get_or_create(
                name='Main Courses', 
                defaults={'is_active': True}
            )[0],
            'Desserts': MenuCategory.objects.get_or_create(
                name='Desserts', 
                defaults={'is_active': True}
            )[0]
        }

        # Menu items data
        menu_items = [
            {
                'name': 'Garlic Bread',
                'description': 'Toasted with garlic butter',
                'price': 5.99,
                'category': 'Appetizers'
            },
            {
                'name': 'Bruschetta',
                'description': 'Toasted bread with tomatoes',
                'price': 7.99,
                'category': 'Appetizers'
            },
            {
                'name': 'Grilled Salmon',
                'description': 'With lemon butter sauce',
                'price': 24.99,
                'category': 'Main Courses'
            },
            {
                'name': 'Pasta Carbonara',
                'description': 'Classic Italian pasta',
                'price': 18.99,
                'category': 'Main Courses'
            },
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Warm with molten center',
                'price': 8.99,
                'category': 'Desserts'
            }
        ]

        # Add menu items
        for item in menu_items:
            if not MenuItem.objects.filter(name=item['name']).exists():
                MenuItem.objects.create(
                    name=item['name'],
                    sku=f"{item['name'].replace(' ', '').upper()[:6]}-{str(uuid.uuid4())[:4]}",
                    description=item['description'],
                    price=item['price'],
                    category=categories[item['category']],
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f"Added {item['name']} to {item['category']}"))
            else:
                self.stdout.write(self.style.WARNING(f"{item['name']} already exists, skipping..."))

        self.stdout.write(self.style.SUCCESS('Successfully added menu items!'))
