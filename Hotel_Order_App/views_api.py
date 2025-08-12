from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related("items").order_by("-created_at")
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["customer_name", "room_number", "status"]
