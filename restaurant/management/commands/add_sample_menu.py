from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Add sample menu categories and items to the database'

    def handle(self, *args, **options):
        # Create or get categories
        categories = [
            {
                'name': 'Appetizers',
                'description': 'Delicious starters to begin your meal',
                'image': 'menu_items/Anytime-Chicken-Breast-in-white-wine-sauce_5.webp'
            },
            {
                'name': 'Main Courses',
                'description': 'Hearty and satisfying main dishes',
                'image': 'menu_items/MSG-Smash-Burger-FT-RECIPE0124-d9682401f3554ef683e24311abdf342b.jpg'
            },
            {
                'name': 'Desserts',
                'description': 'Sweet endings to your meal',
                'image': 'menu_items/Donuts-with-chocolate-glaze-500x500.jpg'
            }
        ]

        # Sample menu items for each category
        menu_items = {
            'Appetizers': [
                {'name': 'Bruschetta', 'description': 'Toasted bread topped with tomatoes, garlic, and fresh basil', 'price': 8.99, 'image': 'menu_items/Anytime-Chicken-Breast-in-white-wine-sauce_5.webp'},
                {'name': 'Calamari', 'description': 'Crispy fried squid served with marinara sauce', 'price': 12.99, 'image': 'menu_items/Anytime-Chicken-Breast-in-white-wine-sauce_5.webp'},
                {'name': 'Spinach Artichoke Dip', 'description': 'Creamy dip served with tortilla chips', 'price': 10.99, 'image': 'menu_items/Anytime-Chicken-Breast-in-white-wine-sauce_5.webp'}
            ],
            'Main Courses': [
                {'name': 'Grilled Salmon', 'description': 'Fresh salmon fillet with lemon butter sauce', 'price': 24.99, 'image': 'menu_items/MSG-Smash-Burger-FT-RECIPE0124-d9682401f3554ef683e24311abdf342b.jpg'},
                {'name': 'Ribeye Steak', 'description': '12oz ribeye cooked to perfection with mashed potatoes', 'price': 29.99, 'image': 'menu_items/MSG-Smash-Burger-FT-RECIPE0124-d9682401f3554ef683e24311abdf342b.jpg'},
                {'name': 'Mushroom Risotto', 'description': 'Creamy arborio rice with wild mushrooms and parmesan', 'price': 18.99, 'image': 'menu_items/MSG-Smash-Burger-FT-RECIPE0124-d9682401f3554ef683e24311abdf342b.jpg'}
            ],
            'Desserts': [
                {'name': 'Chocolate Lava Cake', 'description': 'Warm chocolate cake with a molten center, served with vanilla ice cream', 'price': 8.99, 'image': 'menu_items/Donuts-with-chocolate-glaze-500x500.jpg'},
                {'name': 'New York Cheesecake', 'description': 'Classic cheesecake with strawberry topping', 'price': 7.99, 'image': 'menu_items/Donuts-with-chocolate-glaze-500x500.jpg'},
                {'name': 'Tiramisu', 'description': 'Italian coffee-flavored dessert', 'price': 9.99, 'image': 'menu_items/Donuts-with-chocolate-glaze-500x500.jpg'}
            ]
        }

        # Create categories and menu items
        for category_data in categories:
            category, created = MenuCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            
            # Add image if it exists
            image_path = os.path.join('media', category_data['image'])
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    category.image.save(os.path.basename(image_path), File(img_file), save=True)
            
            self.stdout.write(self.style.SUCCESS(f'Created/Updated category: {category.name}'))
            
            # Add menu items for this category
            for item_data in menu_items[category.name]:
                item, created = MenuItem.objects.get_or_create(
                    name=item_data['name'],
                    category=category,
                    defaults={
                        'description': item_data['description'],
                        'price': item_data['price'],
                        'is_active': True,
                        'sku': f"{category.name[:3].upper()}-{item_data['name'][:3].upper()}-001"
                    }
                )
                
                # Add image if it exists
                image_path = os.path.join('media', item_data['image'])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        item.image.save(os.path.basename(image_path), File(img_file), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'  - Added menu item: {item.name} (${item.price})'))
        
        self.stdout.write(self.style.SUCCESS('Successfully added sample menu data!'))
