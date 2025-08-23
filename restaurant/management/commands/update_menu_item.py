from django.core.management.base import BaseCommand
from restaurant.models import MenuItem, MenuCategory
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Update or create a menu item with an image'

    def handle(self, *args, **options):
        # Get or create a category
        category, created = MenuCategory.objects.get_or_create(
            name='Pizzas',
            defaults={
                'description': 'Delicious wood-fired pizzas',
                'display_order': 1
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created new category: Pizzas'))
        
        # Update or create the menu item
        image_path = os.path.join('media', 'menu_items', 'pizza 1.webp')
        
        if not os.path.exists(image_path):
            self.stdout.write(self.style.ERROR(f'Image not found at {image_path}'))
            return
        
        with open(image_path, 'rb') as img_file:
            menu_item, created = MenuItem.objects.update_or_create(
                name='Margherita Pizza',
                category=category,
                defaults={
                    'description': 'Classic pizza with tomato sauce, mozzarella, and basil',
                    'price': 12.99,
                    'is_active': True,
                    'sku': 'PIZZA-MARG-001'
                }
            )
            
            # Only save the image if it's a new record or if we want to update the image
            if created or not menu_item.image or 'update_image' in options:
                menu_item.image.save(
                    'margherita_pizza.webp',
                    File(img_file),
                    save=True
                )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created new menu item: Margherita Pizza'))
            else:
                self.stdout.write(self.style.SUCCESS('Updated existing menu item: Margherita Pizza'))
                
            self.stdout.write(self.style.SUCCESS(f'Image set from: {image_path}'))
