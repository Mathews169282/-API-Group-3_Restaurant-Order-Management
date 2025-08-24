#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import User

def update_admin2_user():
    """Update existing admin2 user to be superuser and staff"""
    
    User = get_user_model()
    
    # Check if user exists
    email = 'admin@restaurant.com'
    first_name = 'admin2'
    
    try:
        user = User.objects.get(email=email, first_name=first_name)
        print(f"Found user: {email} (Name: {user.first_name})")
        print(f"Current status - Superuser: {user.is_superuser}, Staff: {user.is_staff}, Active: {user.is_active}")
        
        # Update user to be superuser and staff
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f"✅ Successfully updated user: {email}")
        print(f"   - Email: {user.email}")
        print(f"   - First Name: {user.first_name}")
        print(f"   - Superuser: {user.is_superuser}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Active: {user.is_active}")
        
        return user
        
    except User.DoesNotExist:
        print(f"❌ Error: User with email '{email}' and first_name '{first_name}' does not exist!")
        print("Available users:")
        for user in User.objects.all():
            print(f"   - Email: {user.email}, First Name: {user.first_name}, Last Name: {user.last_name}")
        return None

def list_all_users():
    """List all users in the system"""
    User = get_user_model()
    users = User.objects.all()
    
    print("\n📋 All Users in System:")
    print("-" * 50)
    
    for user in users:
        print(f"Email: {user.email}")
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"Superuser: {user.is_superuser}")
        print(f"Staff: {user.is_staff}")
        print(f"Active: {user.is_active}")
        print(f"Last Login: {user.last_login}")
        print("-" * 30)

if __name__ == '__main__':
    print("🔧 Updating Admin2 User Permissions...")
    
    # Update admin2 user to superuser and staff
    admin_user = update_admin2_user()
    
    if admin_user:
        # List all users to confirm changes
        list_all_users()
        
        print("\n✅ Admin2 user update complete!")
        print("\nAdmin2 user now has:")
        print("- Superuser privileges (can access admin panel)")
        print("- Staff privileges (can manage restaurant operations)")
        print("- Active status")
        print("\nYou can now:")
        print("1. Login to admin panel at: http://127.0.0.1:8000/admin/")
        print("2. Use email: admin2@restaurant.com")
        print("3. Access all admin features and manage the restaurant")
    else:
        print("\n❌ Failed to update admin2 user. Please check if the user exists.")
