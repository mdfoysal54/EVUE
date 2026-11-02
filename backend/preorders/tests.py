from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from catalog.models import Category, Product
from .models import Release, PreorderRequest
from .services import reserve_preorder, cancel_request

class PreorderServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='preorder_tester', password='safe-test-pass-123')
        cat = Category.objects.create(name='Upcoming', slug='upcoming-test')
        product = Product.objects.create(category=cat, name='Upcoming Coat', slug='upcoming-coat-test', price=Decimal('1200.00'))
        now = timezone.now()
        self.release = Release.objects.create(product=product, state='preorder', reveal_at=now-timedelta(days=2), opens_at=now-timedelta(days=1), closes_at=now+timedelta(days=1), expected_ship_start=(now+timedelta(days=30)).date(), expected_ship_end=(now+timedelta(days=45)).date(), allocation=3, per_customer_limit=2)

    def test_idempotent_reservation_and_cancel(self):
        req, created = reserve_preorder(release_id=self.release.pk, customer=self.user, quantity=2, idempotency_key='request-12345')
        self.assertTrue(created)
        again, created = reserve_preorder(release_id=self.release.pk, customer=self.user, quantity=2, idempotency_key='request-12345')
        self.assertFalse(created)
        self.assertEqual(req.pk, again.pk)
        self.release.refresh_from_db()
        self.assertEqual(self.release.reserved, 2)
        cancel_request(request_id=req.pk, customer=self.user)
        self.release.refresh_from_db()
        self.assertEqual(self.release.reserved, 0)

    def test_customer_limit(self):
        reserve_preorder(release_id=self.release.pk, customer=self.user, quantity=2, idempotency_key='request-abcde')
        with self.assertRaises(ValidationError):
            reserve_preorder(release_id=self.release.pk, customer=self.user, quantity=1, idempotency_key='request-fghij')
