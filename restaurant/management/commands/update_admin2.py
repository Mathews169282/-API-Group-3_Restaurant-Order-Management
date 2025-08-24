from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Update admin2 user to superuser and staff'

    def handle(self, *args, **options):
        User = get_user_model()
        
        email = 'admin@restaurant.com'
        first_name = 'admin2'
        
        try:
            user = User.objects.get(email=email, first_name=first_name)
            
            self.stdout.write(f"Found user: {user.email} (Name: {user.first_name})")
            self.stdout.write(f"Current status - Superuser: {user.is_superuser}, Staff: {user.is_staff}, Active: {user.is_active}")
            
            # Update user to be superuser and staff
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Successfully updated user: {email}")
            )
            self.stdout.write(f"   - Email: {user.email}")
            self.stdout.write(f"   - First Name: {user.first_name}")
            self.stdout.write(f"   - Superuser: {user.is_superuser}")
            self.stdout.write(f"   - Staff: {user.is_staff}")
            self.stdout.write(f"   - Active: {user.is_active}")
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Error: User with email '{email}' and first_name '{first_name}' does not exist!")
            )
            self.stdout.write("Available users:")
            for user in User.objects.all():
                self.stdout.write(f"   - Email: {user.email}, First Name: {user.first_name}, Last Name: {user.last_name}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating user: {str(e)}")
            )
