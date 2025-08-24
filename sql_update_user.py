#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from django.db import connection

def run_sql_update(sql_query):
    """Execute SQL update query"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            rows_affected = cursor.rowcount
            print(f"✅ Query executed successfully!")
            print(f"   Rows affected: {rows_affected}")
            return rows_affected
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return None

def update_admin2_to_superuser():
    """Update admin2 user to superuser and staff"""
    sql = """
    UPDATE restaurant_user 
    SET is_superuser = 1, is_staff = 1, is_active = 1
    WHERE email = 'admin@restaurant.com' AND first_name = 'admin2';
    """
    print("🔄 Updating admin2 to superuser and staff...")
    return run_sql_update(sql)

def check_user_status():
    """Check current user status"""
    sql = """
    SELECT email, first_name, is_superuser, is_staff, is_active 
    FROM restaurant_user 
    WHERE email = 'admin@restaurant.com';
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            print("👤 Current user status:")
            for row in rows:
                email, first_name, is_superuser, is_staff, is_active = row
                print(f"   Email: {email}")
                print(f"   Name: {first_name}")
                print(f"   Superuser: {bool(is_superuser)}")
                print(f"   Staff: {bool(is_staff)}")
                print(f"   Active: {bool(is_active)}")
    except Exception as e:
        print(f"❌ Error checking user: {e}")

if __name__ == "__main__":
    print("📊 Checking current status...")
    check_user_status()
    
    print("\n🔄 Updating user...")
    result = update_admin2_to_superuser()
    
    if result is not None:
        print("\n📊 New status:")
        check_user_status()
    else:
        print("❌ Update failed!")
