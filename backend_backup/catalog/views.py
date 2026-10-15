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
        return qs

class ProductDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    lookup_field = "slug"
    queryset = Product.objects.filter(active=True).select_related("category")
