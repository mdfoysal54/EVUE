from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "currency", "image_url", "featured", "category"]
