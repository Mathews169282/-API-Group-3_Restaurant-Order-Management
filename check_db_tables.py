import os
import sys
import django

def setup_django():
    """Setup Django environment"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
    django.setup()

def check_tables():
    """Check database tables"""
    from django.db import connection
    
    print("Database tables:")
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
    
    print("\nChecking menu data...")
    from restaurant.models import MenuCategory, MenuItem
    
    categories = MenuCategory.objects.all()
    print(f"\nFound {categories.count()} categories:")
    for cat in categories:
        print(f"- {cat.name} (ID: {cat.id}, Active: {cat.is_active})")
        items = MenuItem.objects.filter(category=cat)
        for item in items:
            print(f"  - {item.name} (${item.price})")

if __name__ == "__main__":
    setup_django()
    check_tables()
