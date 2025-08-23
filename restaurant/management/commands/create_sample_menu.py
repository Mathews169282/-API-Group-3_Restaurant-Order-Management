from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Creates sample menu categories and items for testing'

    def handle(self, *args, **options):
        # Create or get categories
        appetizers, created = MenuCategory.objects.get_or_create(
            name='Appetizers',
            defaults={
                'description': 'Delicious starters to begin your meal',
                'is_active': True
            }
        )
        
        main_courses, created = MenuCategory.objects.get_or_create(
            name='Main Courses',
            defaults={
                'description': 'Hearty and satisfying main dishes',
                'is_active': True
            }
        )
        
        desserts, created = MenuCategory.objects.get_or_create(
            name='Desserts',
            defaults={
                'description': 'Sweet treats to end your meal',
                'is_active': True
            }
        )
        
        # Create sample menu items
        menu_items = [
            {
                'name': 'Garlic Bread',
                'description': 'Toasted bread with garlic butter',
                'price': 5.99,
                'category': appetizers,
                'is_active': True
            },
            {
                'name': 'Bruschetta',
                'description': 'Toasted bread topped with tomatoes, garlic, and fresh basil',
                'price': 7.99,
                'category': appetizers,
                'is_active': True
            },
            {
                'name': 'Grilled Salmon',
                'description': 'Fresh salmon fillet with lemon butter sauce',
                'price': 24.99,
                'category': main_courses,
                'is_active': True
            },
            {
                'name': 'Pasta Carbonara',
                'description': 'Creamy pasta with bacon and parmesan',
                'price': 18.99,
                'category': main_courses,
                'is_active': True
            },
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Warm chocolate cake with a molten center',
                'price': 8.99,
                'category': desserts,
                'is_active': True
            },
            {
                'name': 'New York Cheesecake',
                'description': 'Classic cheesecake with strawberry topping',
                'price': 7.99,
                'category': desserts,
                'is_active': True
            },
        ]
        
        # Create menu items
        for item_data in menu_items:
            item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                category=item_data['category'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price'],
                    'is_active': item_data['is_active'],
                    'sku': f"{item_data['category'].name[:3].upper()}-{item_data['name'][:3].upper()}-001"
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created menu item: {item.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Menu item already exists: {item.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample menu data!'))
