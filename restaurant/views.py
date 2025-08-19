from django.shortcuts import render
from .models import MenuCategory, MenuItem

def menu_list(request):
    categories = MenuCategory.objects.prefetch_related('menuitem_set').all()
    context = {
        'categories': categories,
    }
    return render(request, 'restaurant/menu_list.html', context)
