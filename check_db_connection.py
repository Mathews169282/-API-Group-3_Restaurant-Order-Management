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

def check_connection():
    """Check database connection and print basic info"""
    from django.db import connection
    
    print("=== Database Connection Check ===")
    print(f"Database: {connection.settings_dict['NAME']}")
    print(f"Database exists: {os.path.exists(connection.settings_dict['NAME'])}")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            print(f"SQLite version: {version[0]}")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table[0]}")
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    setup_django()
    check_connection()
