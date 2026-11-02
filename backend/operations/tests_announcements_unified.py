from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Announcement

class AnnouncementPublishingTests(TestCase):
    def test_draft_never_public(self):
        Announcement.objects.create(title='Draft',body='Hidden',published=False)
        self.assertEqual(self.client.get('/api/operations/announcements/').json()['results'],[])
    def test_schedule_window(self):
        now=timezone.now()
        Announcement.objects.create(title='Future',body='Soon',published=True,publish_from=now+timedelta(days=1))
        Announcement.objects.create(title='Expired',body='Past',published=True,publish_until=now-timedelta(seconds=1))
        Announcement.objects.create(title='Current',body='Live',published=True,publish_from=now-timedelta(days=1),publish_until=now+timedelta(days=1))
        self.assertEqual([x['title'] for x in self.client.get('/api/operations/announcements/').json()['results']],['Current'])
    def test_newsletter_requires_consent(self):
        response=self.client.post('/api/operations/newsletter/subscribe/',data='{"email":"test@example.com","consent":false}',content_type='application/json')
        self.assertEqual(response.status_code,400)