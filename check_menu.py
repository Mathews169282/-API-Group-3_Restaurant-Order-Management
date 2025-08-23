import os
import sys
import logging
from tabulate import tabulate
import django

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_check.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_django():
    """Set up Django environment."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
        django.setup()
        logger.info("Django environment set up successfully.")
            print(f"SQLite version: {version[0]}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # List all tables in the database
    print("\nTables in database:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                print(f"- {table[0]}")
    except Exception as e:
        print(f"Error listing tables: {e}")
    
    # Check if menu categories exist
    print("\nMenu Categories:")
    try:
        categories = MenuCategory.objects.all()
        if categories.exists():
            for cat in categories:
                print(f"- {cat.name} (ID: {cat.id}, Active: {cat.is_active})")
        else:
            print("No categories found.")
    except Exception as e:
        print(f"Error fetching categories: {e}")
    
    # Check if menu items exist
    print("\nMenu Items:")
    try:
        items = MenuItem.objects.all()
        if items.exists():
            for item in items:
                print(f"- {item.name} (${item.price}) - {item.category.name if item.category else 'No Category'}")
        else:
            print("No menu items found.")
    except Exception as e:
        print(f"Error fetching menu items: {e}")

if __name__ == "__main__":
    check_menu()
