from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from catalog.models import Category, Product
from .models import CartItem, Order, Stock
from .services import CheckoutError, create_order, cancel_order

class CommerceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="buyer", password="long-test-password-123")
        cat = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(category=cat, name="Silk Dress", slug="silk-dress", price=Decimal("1250.00"), currency="BDT")
        self.stock = Stock.objects.create(product=self.product, on_hand=2)
    def test_checkout_uses_database_price_and_reserves(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        order = create_order(self.user)
        self.assertEqual(order.total, Decimal("2500.00"))
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.reserved, 2)
        self.assertEqual(order.status, Order.Status.PENDING)
    def test_cannot_oversell(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=3)
        with self.assertRaises(CheckoutError): create_order(self.user)
        self.assertFalse(Order.objects.exists())
    def test_cancel_releases_once(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        order = create_order(self.user)
        cancel_order(self.user, order.pk)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.reserved, 0)
        with self.assertRaises(CheckoutError): cancel_order(self.user, order.pk)
    def test_anonymous_denied(self):
        self.assertEqual(self.client.get("/api/commerce/orders/").status_code, 401)
    def test_other_user_cannot_see_order(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        order = create_order(self.user)
        other = get_user_model().objects.create_user(username="other",password="long-test-password-456")
        self.client.force_login(other)
        self.assertEqual(self.client.get(f"/api/commerce/orders/{order.pk}/").status_code, 404)
