import sqlite3

def check_database():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n=== Database Tables ===")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check menu categories
        print("\n=== Menu Categories ===")
        cursor.execute("SELECT id, name, is_active FROM restaurant_menucategory")
        categories = cursor.fetchall()
        for cat in categories:
            print(f"ID: {cat[0]}, Name: {cat[1]}, Active: {bool(cat[2])}")
        
        # Check menu items
        print("\n=== Menu Items ===")
        cursor.execute("""
            SELECT m.id, m.name, m.price, c.name as category, m.sku
            FROM restaurant_menuitem m
            JOIN restaurant_menucategory c ON m.category_id = c.id
        """)
        items = cursor.fetchall()
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[2]}, Category: {item[3]}, SKU: {item[4]}")
        
        print(f"\nTotal categories: {len(categories)}")
        print(f"Total menu items: {len(items)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
