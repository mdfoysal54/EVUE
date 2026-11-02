from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .collection_models import Collection


class CollectionVisibilityTests(TestCase):
    def test_draft_is_hidden(self):
        Collection.objects.create(name="Draft", slug="draft", active=False)
        response = self.client.get("/api/catalog/collections/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("draft", str(response.content))
        self.assertEqual(self.client.get("/api/catalog/collections/draft/products/").status_code, 404)

    def test_scheduled_collection_is_hidden(self):
        Collection.objects.create(name="Future", slug="future", active=True, publish_from=timezone.now() + timedelta(days=1))
        self.assertEqual(self.client.get("/api/catalog/collections/future/products/").status_code, 404)

    def test_published_collection_is_visible(self):
        Collection.objects.create(name="Now", slug="now", active=True, publish_from=timezone.now() - timedelta(days=1))
        self.assertEqual(self.client.get("/api/catalog/collections/now/products/").status_code, 200)