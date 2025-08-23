import os
import sys
import logging
from tabulate import tabulate
import django
from django.db.models import Count, Avg, Min, Max, Sum
from django.core.management.color import color_style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('menu_export.log')
    ]
)
logger = logging.getLogger(__name__)
style = color_style()

def setup_django():
    """Set up Django environment."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurant_Order.settings')
        django.setup()
        logger.info("Django environment set up successfully.")
    except Exception as e:
        logger.error(f"Failed to set up Django: {e}")
        sys.exit(1)

def get_menu_statistics():
    """Get statistics about the menu."""
    from restaurant.models import MenuCategory, MenuItem
    
    stats = {
        'categories': MenuCategory.objects.count(),
        'active_categories': MenuCategory.objects.filter(is_active=True).count(),
        'total_items': MenuItem.objects.count(),
        'active_items': MenuItem.objects.filter(is_active=True).count(),
        'price_stats': MenuItem.objects.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            total_value=Sum('price')
        )
    }
    return stats

def export_menu(format='table'):
    """Export menu data in the specified format."""
    from restaurant.models import MenuCategory, MenuItem
    
    # Get all active categories with their items
    categories = MenuCategory.objects.filter(is_active=True).order_by('name')
    
    if not categories.exists():
        logger.warning("No active categories found in the menu.")
        return
    
    menu_data = []
    
    for category in categories:
        # Add category header
        menu_data.append({
            'type': 'category',
            'name': category.name.upper(),
            'description': '',
            'price': '',
            'status': 'Active' if category.is_active else 'Inactive'
        })
        
        # Get active items for this category
        items = MenuItem.objects.filter(
            category=category,
            is_active=True
        ).order_by('name')
        
        for item in items:
            menu_data.append({
                'type': 'item',
                'name': f"  {item.name}",
                'description': item.description or 'No description',
                'price': f"${item.price:.2f}",
                'status': 'Active' if item.is_active else 'Inactive'
            })
        if items:
            print("\n  Items:")
            for item in items:
                print(f"  - {item.name} (ID: {item.id}, ${item.price}, Active: {item.is_active})")
                print(f"    Description: {item.description}")
        else:
            print("  No items in this category")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total categories: {categories.count()}")
    print(f"Total menu items: {MenuItem.objects.count()}")

if __name__ == "__main__":
    list_menu_data()
