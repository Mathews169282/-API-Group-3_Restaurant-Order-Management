import os
import django
import sys

# Set up Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
django.setup()

from restaurant.models import MenuItem

def map_images_to_menu_items():
    # Get all menu items
    menu_items = MenuItem.objects.all()
    
    # Get all image files in the media/menu_items directory
    media_dir = os.path.join(BASE_DIR, 'media', 'menu_items')
    if not os.path.exists(media_dir):
        print(f"Media directory not found: {media_dir}")
        return
    
    image_files = [f for f in os.listdir(media_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    print(f"Found {len(image_files)} image files in media directory")
    
    # Create a mapping of item names to their closest matching image
    name_mapping = {
        'pizza': 'pizza',
        'burger': 'burger',
        'pasta': 'pasta',
        'salad': 'salad',
        'soup': 'soup',
        'chicken': 'chicken',
        'beef': 'beef',
        'fish': 'salmon',
        'rice': 'rice',
        'noodles': 'noodles',
        'sandwich': 'sandwich',
        'fries': 'fries',
        'ice cream': 'icecream',
        'cake': 'cake',
        'pancake': 'pancake',
        'smoothie': 'smoothie',
        'pizza': 'pizza',
        'burger': 'burger',
        'pasta': 'pasta',
        'salad': 'salad',
        'soup': 'soup',
        'chicken': 'chicken',
        'beef': 'beef',
        'fish': 'salmon',
        'rice': 'rice',
        'noodles': 'noodles',
        'sandwich': 'sandwich',
        'fries': 'fries',
        'ice cream': 'icecream',
        'cake': 'cake',
        'pancake': 'pancake',
        'smoothie': 'smoothie'
    }
    
    # Update menu items with matching images
    updated_count = 0
    for item in menu_items:
        item_name = item.name.lower()
        
        # Try to find a matching image
        matched_image = None
        
        # First, try exact match with item name
        for img in image_files:
            img_name = os.path.splitext(img)[0].lower()
            if item_name in img_name or img_name in item_name:
                matched_image = img
                break
        
        # If no exact match, try with name mapping
        if not matched_image:
            for keyword, img_keyword in name_mapping.items():
                if keyword in item_name:
                    for img in image_files:
                        if img_keyword in img.lower():
                            matched_image = img
                            break
                    if matched_image:
                        break
        
        # If still no match, use default image
        if not matched_image:
            print(f"No matching image found for: {item.name}")
            continue
        
        # Update the menu item with the image
        image_path = os.path.join('menu_items', matched_image)
        if str(item.image) != image_path:
            item.image = image_path
            item.save()
            updated_count += 1
            print(f"Updated {item.name} with image: {matched_image}")
    
    print(f"\nUpdated {updated_count} menu items with images.")

if __name__ == "__main__":
    map_images_to_menu_items()
