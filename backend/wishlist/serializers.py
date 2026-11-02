from rest_framework import serializers
from catalog.models import Product
from .models import WishlistItem

class WishlistItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    slug = serializers.CharField(source="product.slug", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=12, decimal_places=2, read_only=True)
    currency = serializers.CharField(source="product.currency", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ["id", "product_id", "name", "slug", "price", "currency", "image_url", "created_at"]

    def get_image_url(self, obj):
        image = getattr(obj.product, "image", None)
        if image:
            request = self.context.get("request")
            return request.build_absolute_uri(image.url) if request else image.url
        return obj.product.image_url or ""

class AddWishlistSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(active=True), source="product")
