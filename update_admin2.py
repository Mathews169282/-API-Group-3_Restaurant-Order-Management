#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from django.contrib.auth import get_user_model

def update_admin2():
    """Update admin2 to be superuser and staff"""
    User = get_user_model()
    
    try:
        # Find admin2 user
        user = User.objects.get(email='admin2@restaurant.com')
        
        print(f"Found user: {user.email}")
        print(f"Before - Superuser: {user.is_superuser}, Staff: {user.is_staff}")
        
        # Update permissions
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        
        print(f"After - Superuser: {user.is_superuser}, Staff: {user.is_staff}")
        print("✅ Admin2 successfully updated!")
        
    except User.DoesNotExist:
        print("❌ admin2@restaurant.com user not found!")
        
        # List existing users
        users = User.objects.all()
        print("\nExisting users:")
        for u in users:
            print(f"- {u.email} (Super: {u.is_superuser}, Staff: {u.is_staff})")

if __name__ == '__main__':
    update_admin2()
