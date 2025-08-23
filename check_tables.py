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

def list_tables():
    """List all tables in the database"""
    from django.db import connection
    
    print("=== Database Tables ===")
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
            
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 50)
            
            try:
                # Try to get the first few rows from the table
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                
                if not rows:
                    print("  (No data)")
                    continue
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                print("  " + " | ".join(columns))
                print("  " + "-" * 50)
                
                # Print rows
                for row in rows:
                    print("  " + " | ".join(str(value) for value in row))
                
                # Count total rows
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                if count > 5:
                    print(f"  ... and {count - 5} more rows")
                
            except Exception as e:
                print(f"  Error reading table: {e}")

if __name__ == "__main__":
    setup_django()
    list_tables()
