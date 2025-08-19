import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
import django
django.setup()

from restaurant.models import MenuCategory, MenuItem

def add_kenyan_menu():
    print("Adding Kenyan menu items...")
    
    # Create categories if they don't exist
    categories = {
        'Main Dishes': [
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
        ],
        'Sides': [
            {'name': 'Kachumbari', 'price': 150, 'sku': 'KCH001'},
            {'name': 'Sukuma Wiki', 'price': 100, 'sku': 'SWK001'},
            {'name': 'Chips Masala', 'price': 250, 'sku': 'CHM001'},
            {'name': 'Kachumbari Special', 'price': 200, 'sku': 'KCS001'},
            {'name': 'Steamed Vegetables', 'price': 150, 'sku': 'STV001'},
        ],
        'Beverages': [
            {'name': 'Dawa Cocktail', 'price': 450, 'sku': 'DAW001'},
            {'name': 'Masala Chai', 'price': 150, 'sku': 'MCH001'},
            {'name': 'Mango Juice (Fresh)', 'price': 250, 'sku': 'MGF001'},
            {'name': 'Soda (500ml)', 'price': 120, 'sku': 'SOD001'},
            {'name': 'African Tea', 'price': 150, 'sku': 'AFT001'},
            {'name': 'Passion Juice (Fresh)', 'price': 250, 'sku': 'PJF001'},
            {'name': 'Mineral Water (500ml)', 'price': 100, 'sku': 'WAT001'},
        ],
        'Desserts': [
            {'name': 'Mahamri (3pcs)', 'price': 100, 'sku': 'MHM001'},
            {'name': 'Mandazi (3pcs)', 'price': 80, 'sku': 'MDZ001'},
            {'name': 'Fruit Salad', 'price': 300, 'sku': 'FRS001'},
            {'name': 'Ice Cream (Scoop)', 'price': 150, 'sku': 'ICS001'},
        ]
    }
    
    for category_name, items in categories.items():
        # Get or create category
        category, created = MenuCategory.objects.get_or_create(
            name=category_name,
            defaults={'is_active': True}
        )
        
        if created:
            print(f"Created category: {category_name}")
        
        # Add items to category
        for item in items:
            MenuItem.objects.get_or_create(
                sku=item['sku'],
                defaults={
                    'name': item['name'],
                    'price': item['price'],
                    'category': category,
                    'is_active': True,
                    'description': f'Delicious {item["name"]} - a Kenyan favorite!'
                }
            )
            print(f"Added: {item['name']} - KSh {item['price']}")
    
    print("\nKenyan menu has been successfully added!")

if __name__ == "__main__":
    add_kenyan_menu()
