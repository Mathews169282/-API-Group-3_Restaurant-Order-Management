
from django.shortcuts import render, redirect
from datetime import datetime
from .forms import OrderForm

DEMO_ORDERS = [
    {
        "id": 1, "customer_name": "Alice Kim", "room_number": "203",
        "status": "PENDING", "total": 24.50, "created_at": datetime.now(),
        "items": [{"name":"Club Sandwich","qty":1,"price":12.50},
                  {"name":"Tea","qty":2,"price":6.00}],
        "notes": "No onions"
    },
    {
        "id": 2, "customer_name": "John Doe", "room_number": "110",
        "status": "COMPLETED", "total": 18.00, "created_at": datetime.now(),
        "items": [{"name":"Pasta","qty":1,"price":12.00},
                  {"name":"Soda","qty":1,"price":6.00}],
        "notes": ""
    },
]

def Home(request):
    stats = {
        "total_orders": len(DEMO_ORDERS),
        "pending": sum(1 for o in DEMO_ORDERS if o["status"] == "PENDING"),
        "completed": sum(1 for o in DEMO_ORDERS if o["status"] == "COMPLETED"),
    }
    recent = sorted(DEMO_ORDERS, key=lambda o: o["created_at"], reverse=True)[:5]
    return render(request, "Restaurant_Order_App/Home.html", {"stats": stats, "recent_orders": recent})

def Order_list(request):
    return render(request, "Restaurant_Order_App/Order_list.html", {"orders": DEMO_ORDERS})

def Order_detail(request, pk):
    order = next((o for o in DEMO_ORDERS if o["id"] == pk), None)
    return render(request, "Restaurant_Order_App/Order_detail.html", {"order": order})


def Order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user if request.user.is_authenticated else None
            order.save()
            order.recalc_totals()
            return redirect("Order_detail", pk=order.pk)
    else:
        form = OrderForm()
    return render(request, "Restaurant_Order_App/Order_form.html", {"form": form})

def Order_edit(request, pk):
    return render(request, "Restaurant_Order_App/Order_form.html", {"form": type("F", (), {"instance": type("I", (), {"pk": pk})()})()})


def Menu_list(request):
   
    return render(request, "Restaurant_Order_App/menu_list.html", {
    
    })

