from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import ShippingZone

class ShippingQuoteTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="shippingtest", password="test-password-123")
        self.client = APIClient()
        ShippingZone.objects.create(name="Dhaka city", city="Dhaka", fee=Decimal("80.00"))

    def test_requires_auth(self):
        self.assertIn(self.client.get("/api/shipping/quote/?city=Dhaka").status_code, (401, 403))

    def test_quote(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/shipping/quote/?city=dhaka")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["shipping_fee"], "80.00")
        self.assertTrue(response.data["estimate_only"])