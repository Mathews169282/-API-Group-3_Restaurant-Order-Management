import os
import sys
import logging
import django
from django.core.management import call_command
from django.db import connection, transaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_setup.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_django():
    """Set up Django environment."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
        django.setup()
        logger.info("Django environment set up successfully.")
    except Exception as e:
        logger.error(f"Failed to set up Django: {e}")
        sys.exit(1)

@transaction.atomic
def reset_database():
    """Reset the database by dropping and recreating it."""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
        if os.path.exists(db_path):
            logger.info("Removing existing database...")
            os.remove(db_path)
        
        logger.info("Running migrations...")
        call_command('migrate', '--noinput')
        
        logger.info("Creating superuser...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            logger.info("Superuser created successfully.")
        else:
            logger.info("Superuser already exists.")
        
        logger.info("Database reset completed successfully.")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise

def create_sample_data():
    """Create sample menu data."""
    from django.contrib.auth import get_user_model
    from restaurant.models import MenuCategory, MenuItem
    
    User = get_user_model()
    
    try:
        # Create test user if not exists
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user('testuser', 'test@example.com', 'testpass123')
            logger.info("Created test user: testuser / testpass123")
        
        # Create categories
        categories = [
            {'name': 'Appetizers', 'is_active': True},
            {'name': 'Main Courses', 'is_active': True},
            {'name': 'Desserts', 'is_active': True},
            {'name': 'Drinks', 'is_active': True},
        ]
        
        for cat_data in categories:
            cat, created = MenuCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'is_active': cat_data['is_active']}
            )
            if created:
                logger.info(f"Created category: {cat.name}")
        
        # Create menu items with more realistic data
        menu_items = [
            {
                'name': 'Garlic Bread',
                'category': 'Appetizers',
                'price': 5.99,
                'is_active': True,
                'description': 'Toasted bread with garlic butter and herbs',
                'image': 'menu_items/garlic_bread.jpg'
            },
            {
                'name': 'Caesar Salad',
                'category': 'Appetizers',
                'price': 8.99,
                'is_active': True,
                'description': 'Fresh romaine lettuce with Caesar dressing and croutons',
                'image': 'menu_items/caesar_salad.jpg'
            },
            {
                'name': 'Grilled Salmon',
                'category': 'Main Courses',
                'price': 22.99,
                'is_active': True,
                'description': 'Fresh salmon fillet with lemon butter sauce',
                'image': 'menu_items/grilled_salmon.jpg'
            },
            {
                'name': 'Pasta Carbonara',
                'category': 'Main Courses',
                'price': 18.99,
                'is_active': True,
                'description': 'Classic Italian pasta with pancetta and egg sauce',
                'image': 'menu_items/pasta_carbonara.jpg'
            },
            {
                'name': 'Chocolate Lava Cake',
                'category': 'Desserts',
                'price': 7.99,
                'is_active': True,
                'description': 'Warm chocolate cake with a molten center',
                'image': 'menu_items/chocolate_lava_cake.jpg'
            },
            {
                'name': 'Iced Tea',
                'category': 'Drinks',
                'price': 3.99,
                'is_active': True,
                'description': 'Freshly brewed iced tea with lemon',
                'image': 'menu_items/iced_tea.jpg'
            },
        ]
        
        for item_data in menu_items:
            category = MenuCategory.objects.get(name=item_data.pop('category'))
            item, created = MenuItem.objects.get_or_create(
                category=category,
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                logger.info(f"Created menu item: {item.name} (${item.price})")
            
        logger.info("Sample data creation completed successfully.")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        raise

def main():
    """Main function to execute the script."""
    try:
        logger.info("Starting menu setup process...")
        setup_django()
        reset_database()
        create_sample_data()
        
        logger.info("\n=== Setup Completed Successfully ===")
        logger.info("Admin: username=admin (check your Django settings for password)")
        logger.info("Test User: username=testuser / password=testpass123")
        logger.info("Access admin at: http://localhost:8000/admin/")
        logger.info("View menu at: http://localhost:8000/menu/")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("Sample data added successfully!")

if __name__ == "__main__":
    setup_django()
    reset_database()
    add_sample_data()
    print("\nSetup complete! You can now run the development server with:")
    print("python manage.py runserver")
    print("\nAdmin credentials:")
    print("Username: admin")
    print("Password: admin123")
