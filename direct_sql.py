import sqlite3
import uuid

def add_menu_items():
    # Connect to the SQLite database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Add categories if they don't exist
        categories = {}
        for name in ['Appetizers', 'Main Courses', 'Desserts']:
            cursor.execute("SELECT id FROM restaurant_menucategory WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if not result:
                cursor.execute(
                    "INSERT INTO restaurant_menucategory (name, is_active, created_at, updated_at) VALUES (?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (name,)
                )
                category_id = cursor.lastrowid
                print(f"Created category: {name} (ID: {category_id})")
            else:
                category_id = result[0]
                print(f"Category exists: {name} (ID: {category_id})")
            
            categories[name] = category_id
        
        # Menu items to add
        menu_items = [
            ('Garlic Bread', 'Toasted with garlic butter', 5.99, 'Appetizers'),
            ('Bruschetta', 'Toasted bread with tomatoes', 7.99, 'Appetizers'),
            ('Grilled Salmon', 'With lemon butter sauce', 24.99, 'Main Courses'),
            ('Pasta Carbonara', 'Classic Italian pasta', 18.99, 'Main Courses'),
            ('Chocolate Lava Cake', 'Warm with molten center', 8.99, 'Desserts')
        ]
        
        # Add menu items
        for name, desc, price, category in menu_items:
            cursor.execute("SELECT id FROM restaurant_menuitem WHERE name = ?", (name,))
            if not cursor.fetchone():
                sku = f"{name.replace(' ', '').upper()[:6]}-{str(uuid.uuid4())[:4]}"
                cursor.execute("""
                    INSERT INTO restaurant_menuitem 
                    (name, description, price, sku, is_active, category_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (name, desc, price, sku, categories[category]))
                print(f"Added: {name} (${price})")
            else:
                print(f"Skipped (exists): {name}")
        
        # Commit changes
        conn.commit()
        print("\nMenu items added successfully!")
        
        # Print summary
        cursor.execute("""
            SELECT c.name, COUNT(m.id) as item_count
            FROM restaurant_menucategory c
            LEFT JOIN restaurant_menuitem m ON c.id = m.category_id
            GROUP BY c.name
        """)
        
        print("\n=== Menu Summary ===")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} items")
            
        cursor.execute("SELECT COUNT(*) FROM restaurant_menuitem")
        print(f"Total items: {cursor.fetchone()[0]}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_menu_items()
