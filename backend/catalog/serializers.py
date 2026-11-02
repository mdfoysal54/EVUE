from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "currency", "image_url", "featured", "category"]

    def get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get("request")
            return request.build_absolute_uri(url) if request else url
        return obj.image_url or ""
