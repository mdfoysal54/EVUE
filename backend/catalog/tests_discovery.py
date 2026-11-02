from django.test import TestCase
from .models import Category, Product

class ProductDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        men = Category.objects.create(name="Men", slug="men")
        women = Category.objects.create(name="Women", slug="women")
        Product.objects.create(category=men, name="Cotton Shirt", slug="cotton-shirt", price="1000", description="Soft cotton")
        Product.objects.create(category=women, name="Silk Dress", slug="silk-dress", price="3000")
        Product.objects.create(category=men, name="Hidden Coat", slug="hidden-coat", price="5000", active=False)

    def test_search_name_and_description(self):
        response = self.client.get("/api/catalog/products/", {"q": "cotton"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["slug"], "cotton-shirt")

    def test_department_and_sort(self):
        response = self.client.get("/api/catalog/products/", {"department": "men", "sort": "price_desc"})
        self.assertEqual(response.json()["count"], 1)

    def test_inactive_not_exposed(self):
        response = self.client.get("/api/catalog/products/", {"q": "Hidden"})
        self.assertEqual(response.json()["count"], 0)

    def test_invalid_sort_defaults_safely(self):
        response = self.client.get("/api/catalog/products/", {"sort": "not-a-field"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)
