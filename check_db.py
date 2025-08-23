import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
    django.setup()

def check_database():
    """Check database connection and tables"""
    from django.db import connection
    
    print("=== Database Check ===")
    print(f"Database: {connection.settings_dict['NAME']}")
    
    # Check if database file exists
    db_path = Path(connection.settings_dict['NAME'])
    print(f"Database exists: {db_path.exists()}")
    
    if not db_path.exists():
        print("\nCreating new database...")
        from django.core.management import call_command
        call_command('migrate')
        print("Database created and migrations applied.")
    
    # Check if tables exist
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
    
    # Check if menu tables exist
    menu_tables = ['restaurant_menucategory', 'restaurant_menuitem']
    missing_tables = [t for t in menu_tables if t not in [t[0] for t in tables]]
    
    if missing_tables:
        print("\nMissing menu tables. Running migrations...")
        from django.core.management import call_command
        call_command('makemigrations')
        call_command('migrate')
        print("Migrations completed.")
    else:
        print("\nAll menu tables exist.")

if __name__ == "__main__":
    setup_django()
    check_database()
