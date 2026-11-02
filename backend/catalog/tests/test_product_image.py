from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from catalog.models import Category, Product
from catalog.serializers import ProductSerializer


@override_settings(MEDIA_ROOT="/tmp/evu-test-product-images")
class ProductImageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test", slug="test")

    def test_old_image_url_fallback(self):
        product = Product.objects.create(category=self.category, name="One", slug="one", price="10.00", image_url="https://example.com/one.jpg")
        self.assertEqual(ProductSerializer(product).data["image_url"], "https://example.com/one.jpg")

    def test_uploaded_image_takes_priority(self):
        product = Product.objects.create(category=self.category, name="Two", slug="two", price="10.00", image_url="https://example.com/old.jpg")
        product.image.name = "products/example.jpg"
        request = APIRequestFactory().get("/api/catalog/products/")
        self.assertEqual(ProductSerializer(product, context={"request": request}).data["image_url"], "http://testserver/media/products/example.jpg")
