from django.core.management.base import BaseCommand
from restaurant.models import MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Seeds the database with Kenyan menu items'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Kenyan menu items...')
        
        # Create or get categories
        main_dishes, _ = MenuCategory.objects.get_or_create(
            name='Main Dishes',
            defaults={'is_active': True}
        )
        
        sides, _ = MenuCategory.objects.get_or_create(
            name='Sides',
            defaults={'is_active': True}
        )
        
        beverages, _ = MenuCategory.objects.get_or_create(
            name='Beverages',
            defaults={'is_active': True}
        )
        
        desserts, _ = MenuCategory.objects.get_or_create(
            name='Desserts',
            defaults={'is_active': True}
        )
        
        # Main Dishes
        main_dish_items = [
            {'name': 'Nyama Choma (Beef)', 'price': 1200, 'sku': 'NCB001'},
            {'name': 'Nyama Choma (Goat)', 'price': 1500, 'sku': 'NCG001'},
            {'name': 'Ugali with Sukuma Wiki', 'price': 300, 'sku': 'USW001'},
            {'name': 'Githeri Special', 'price': 450, 'sku': 'GIT001'},
            {'name': 'Mukimo with Beef Stew', 'price': 600, 'sku': 'MBS001'},
            {'name': 'Chicken Biryani', 'price': 850, 'sku': 'CBY001'},
            {'name': 'Fish Fillet with Ugali', 'price': 900, 'sku': 'FFU001'},
            {'name': 'Pilau with Kachumbari', 'price': 550, 'sku': 'PKC001'},
            {'name': 'Matoke with Beef Stew', 'price': 650, 'sku': 'MBS002'},
            {'name': 'Chapati with Beans', 'price': 350, 'sku': 'CHB001'},
        ]
        
        # Sides
        side_items = [
            {'name': 'Kachumbari', 'price': 150, 'sku': 'KCH001'},
            {'name': 'Sukuma Wiki', 'price': 100, 'sku': 'SWK001'},
            {'name': 'Chips Masala', 'price': 250, 'sku': 'CHM001'},
            {'name': 'Kachumbari Special', 'price': 200, 'sku': 'KCS001'},
            {'name': 'Steamed Vegetables', 'price': 150, 'sku': 'STV001'},
        ]
        
        # Beverages
        beverage_items = [
            {'name': 'Dawa Cocktail', 'price': 450, 'sku': 'DAW001'},
            {'name': 'Masala Chai', 'price': 150, 'sku': 'MCH001'},
            {'name': 'Mango Juice (Fresh)', 'price': 250, 'sku': 'MGF001'},
            {'name': 'Soda (500ml)', 'price': 120, 'sku': 'SOD001'},
            {'name': 'African Tea', 'price': 150, 'sku': 'AFT001'},
            {'name': 'Passion Juice (Fresh)', 'price': 250, 'sku': 'PJF001'},
            {'name': 'Mineral Water (500ml)', 'price': 100, 'sku': 'WAT001'},
        ]
        
        # Desserts
        dessert_items = [
            {'name': 'Mahamri (3pcs)', 'price': 100, 'sku': 'MHM001'},
            {'name': 'Mandazi (3pcs)', 'price': 80, 'sku': 'MDZ001'},
            {'name': 'Fruit Salad', 'price': 300, 'sku': 'FRS001'},
            {'name': 'Ice Cream (Scoop)', 'price': 150, 'sku': 'ICS001'},
        ]
        
        # Create menu items
        def create_menu_items(items, category):
            for item_data in items:
                MenuItem.objects.get_or_create(
                    sku=item_data['sku'],
                    defaults={
                        'name': item_data['name'],
                        'price': item_data['price'],
                        'category': category,
                        'is_active': True,
                        'description': f'Delicious {item_data["name"]} - a Kenyan favorite!'
                    }
                )
        
        # Create all items
        create_menu_items(main_dish_items, main_dishes)
        create_menu_items(side_items, sides)
        create_menu_items(beverage_items, beverages)
        create_menu_items(dessert_items, desserts)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded Kenyan menu items!'))
