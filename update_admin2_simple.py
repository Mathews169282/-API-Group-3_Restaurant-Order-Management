#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from django.contrib.auth import get_user_model

def main():
    User = get_user_model()
    
    print("🔍 Looking for admin2 user...")
    print(f"Email: admin@restaurant.com")
    print(f"First Name: admin2")
    print()
    
    try:
        user = User.objects.get(email='admin@restaurant.com', first_name='admin2')
        print("✅ Found admin2 user!")
        print(f"Current status:")
        print(f"  - Email: {user.email}")
        print(f"  - First Name: {user.first_name}")
        print(f"  - Last Name: {user.last_name}")
        print(f"  - Superuser: {user.is_superuser}")
        print(f"  - Staff: {user.is_staff}")
        print(f"  - Active: {user.is_active}")
        print()
        
        print("🔄 Updating user permissions...")
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print("✅ Update complete!")
        print(f"New status:")
        print(f"  - Superuser: {user.is_superuser}")
        print(f"  - Staff: {user.is_staff}")
        print(f"  - Active: {user.is_active}")
        
    except User.DoesNotExist:
        print("❌ admin2 user not found!")
        print("Available users:")
        for user in User.objects.all():
            print(f"  - Email: {user.email}, First: '{user.first_name}', Last: '{user.last_name}'")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
