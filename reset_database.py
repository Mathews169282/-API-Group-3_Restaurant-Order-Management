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

def reset_database():
    """Reset the database and apply migrations"""
    from django.db import connection
    import sqlite3
    
    # Get database path from settings
    db_path = connection.settings_dict['NAME']
    
    print(f"Resetting database at: {db_path}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print("Removing existing database...")
        os.remove(db_path)
    
    # Create new database and apply migrations
    print("Creating new database and applying migrations...")
    from django.core.management import call_command
    call_command('migrate')
    
    # Create superuser
    print("\nCreating superuser...")
    call_command('createsuperuser', interactive=False, username='admin', email='admin@example.com')
    print("Superuser created with username: admin")
    print("Please set the password when prompted.")
    
    # Load sample data
    print("\nLoading sample data...")
    try:
        call_command('create_sample_menu')
        print("Sample menu data loaded successfully!")
    except Exception as e:
        print(f"Error loading sample data: {e}")
    
    print("\nDatabase reset complete!")

if __name__ == "__main__":
    setup_django()
    reset_database()
