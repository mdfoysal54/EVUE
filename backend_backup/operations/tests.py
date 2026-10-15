from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Announcement

class OperationsTests(TestCase):
    def test_only_published_announcements_are_public(self):
        Announcement.objects.create(title='Visible',body='Hello',published=True)
        Announcement.objects.create(title='Hidden',body='Secret',published=False)
        response=self.client.get('/api/operations/announcements/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()['results']),1)
    def test_reports_require_superuser(self):
        self.assertEqual(self.client.get('/api/operations/reports/').status_code,302)
        u=get_user_model().objects.create_user(username='staffer',password='Strong-Passphrase-2026!',is_staff=True)
        self.client.force_login(u)
        self.assertEqual(self.client.get('/api/operations/reports/').status_code,403)