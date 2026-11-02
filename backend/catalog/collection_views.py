from django.http import Http404
from rest_framework import generics, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from .collection_models import Collection
from .models import Product
from .serializers import ProductSerializer


class CollectionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ["name", "slug", "description", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class CollectionList(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CollectionSerializer
    queryset = Collection.objects.none()

    def get_queryset(self):
        return Collection.visible()


class CollectionProductsPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 48


class CollectionProducts(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    pagination_class = CollectionProductsPagination

    def get_queryset(self):
        slug = self.kwargs["slug"]
        collection = Collection.visible().filter(slug=slug).first()
        if collection is None:
            raise Http404
        return Product.objects.filter(active=True, curated_collections=collection).select_related("category").order_by("name", "id")