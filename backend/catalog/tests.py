from django.test import TestCase
from django.urls import reverse
from .models import Category, Product

class CatalogTests(TestCase):
    def setUp(self):
        c = Category.objects.create(name="Dresses", slug="dresses")
        self.p = Product.objects.create(category=c, name="Silk Dress", slug="silk-dress", price="2999.00")
    def test_public_list(self):
        response = self.client.get("/api/catalog/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
    def test_inactive_hidden(self):
        self.p.active = False
        self.p.save()
        self.assertEqual(self.client.get("/api/catalog/products/").json()["count"], 0)
        self.assertEqual(self.client.get("/api/catalog/products/silk-dress/").status_code, 404)
    def test_health(self):
        self.assertEqual(self.client.get("/api/health/").json()["status"], "ok")
