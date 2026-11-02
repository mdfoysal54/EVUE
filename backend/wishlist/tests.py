import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from catalog.models import Category, Product
from .models import WishlistItem

class WishlistTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="wishuser", password="strong-test-password-123")
        self.other = get_user_model().objects.create_user(username="otherwish", password="strong-test-password-123")
        category = Category.objects.create(name="Wish test", slug="wish-test")
        self.product = Product.objects.create(category=category, name="Shirt", slug="wish-shirt", price=Decimal("100.00"), active=True)
        self.client = APIClient()

    def test_authentication_required(self):
        self.assertIn(self.client.get("/api/wishlist/").status_code, [401, 403])

    def test_add_idempotent_and_delete(self):
        self.client.force_authenticate(self.user)
        payload = {"product_id": str(self.product.pk)}
        self.assertEqual(self.client.post("/api/wishlist/", payload, format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/wishlist/", payload, format="json").status_code, 200)
        self.assertEqual(WishlistItem.objects.count(), 1)
        self.assertEqual(len(self.client.get("/api/wishlist/").data), 1)
        self.assertEqual(self.client.delete(f"/api/wishlist/{self.product.pk}/").status_code, 204)
        self.assertEqual(WishlistItem.objects.count(), 0)

    def test_customer_isolation(self):
        WishlistItem.objects.create(customer=self.other, product=self.product)
        self.client.force_authenticate(self.user)
        self.assertEqual(len(self.client.get("/api/wishlist/").data), 0)
        self.client.delete(f"/api/wishlist/{self.product.pk}/")
        self.assertEqual(WishlistItem.objects.filter(customer=self.other).count(), 1)
