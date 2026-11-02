from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.throttling import AnonRateThrottle
from .models import Product
from .serializers import ProductSerializer

class ProductList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = ProductSerializer
    def get_queryset(self):
        qs = Product.objects.filter(active=True).select_related("category").order_by("-created_at", "id")
        if self.request.query_params.get("featured") == "true":
            qs = qs.filter(featured=True)
        department = self.request.query_params.get("department", "").strip()
        if department:
            qs = qs.filter(category__slug__iexact=department)
        search = self.request.query_params.get("q", "").strip()[:120]
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search))
        category = self.request.query_params.get("category", "").strip()[:100]
        if category:
            qs = qs.filter(category__slug__iexact=category)
        ordering = self.request.query_params.get("sort", "newest")
        orders = {
            "newest": ("-created_at", "id"),
            "price_asc": ("price", "id"),
            "price_desc": ("-price", "id"),
            "name": ("name", "id"),
        }
        return qs.order_by(*orders.get(ordering, orders["newest"]))

class ProductDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    lookup_field = "slug"
    queryset = Product.objects.filter(active=True).select_related("category")
