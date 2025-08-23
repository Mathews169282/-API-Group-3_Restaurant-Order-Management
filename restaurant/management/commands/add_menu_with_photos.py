import os
from django.core.management.base import BaseCommand
from django.core.files import File
from restaurant.models import MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Add sample menu items with categories and photos'

    def handle(self, *args, **options):
        # Create media directory if it doesn't exist
        media_dir = os.path.join('media', 'menu_items')
        os.makedirs(media_dir, exist_ok=True)
        
        # Define categories
        categories = [
            {'name': 'Appetizers', 'description': 'Delicious starters to begin your meal'},
            {'name': 'Main Courses', 'description': 'Hearty and satisfying main dishes'},
            {'name': 'Desserts', 'description': 'Sweet treats to end your meal'},
            {'name': 'Beverages', 'description': 'Refreshing drinks'},
        ]
        
        # Define menu items with sample image URLs (you can replace these with actual image paths)
        menu_items = [
            # Appetizers
            {
                'name': 'Garlic Bread',
                'description': 'Freshly baked bread with garlic and herbs',
                'price': 5.99,
                'category': 'Appetizers',
                'image_url': 'https://example.com/garlic_bread.jpg'  # Placeholder
            },
            {
                'name': 'Bruschetta',
                'description': 'Toasted bread topped with tomatoes, garlic, and basil',
                'price': 7.99,
                'category': 'Appetizers',
                'image_url': 'https://example.com/bruschetta.jpg'  # Placeholder
            },
            # Main Courses
            {
                'name': 'Grilled Salmon',
                'description': 'Fresh salmon fillet with lemon butter sauce',
                'price': 24.99,
                'category': 'Main Courses',
                'image_url': 'https://example.com/salmon.jpg'  # Placeholder
            },
            {
                'name': 'Pasta Carbonara',
                'description': 'Classic Italian pasta with eggs, cheese, and pancetta',
                'price': 18.99,
                'category': 'Main Courses',
                'image_url': 'https://example.com/carbonara.jpg'  # Placeholder
            },
            # Desserts
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Warm chocolate cake with a molten center',
                'price': 8.99,
                'category': 'Desserts',
                'image_url': 'https://example.com/lava_cake.jpg'  # Placeholder
            },
            # Beverages
            {
                'name': 'Iced Tea',
                'description': 'Refreshing iced tea with lemon',
                'price': 3.99,
                'category': 'Beverages',
                'image_url': 'https://example.com/iced_tea.jpg'  # Placeholder
            },
        ]
        
        # Create categories
        category_objs = {}
        for cat_data in categories:
            category, created = MenuCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            category_objs[cat_data['name']] = category
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
        
        # Create menu items
        for item_data in menu_items:
            category = category_objs[item_data['category']]
            item, created = MenuItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price'],
                    'category': category,
                    'is_active': True
                }
            )
            
            # Note: To add actual images, you'll need to download them or use existing ones
            # For now, we're just setting the image URL in the description
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created menu item: {item.name} (${item.price})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated menu item: {item.name} (${item.price})'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample menu data!'))
        self.stdout.write(self.style.WARNING('Note: You may want to add actual images to the media/menu_items directory'))
