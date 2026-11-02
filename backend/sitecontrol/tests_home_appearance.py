from django.test import TestCase
from django.urls import reverse
from .models import SectionAppearance


class PublicHomeAppearanceTests(TestCase):
    def test_home_section_visible_without_login(self):
        SectionAppearance.objects.create(
            page='home', section='hero', heading='New EVU Edit', subtitle='New season', enabled=True
        )
        response = self.client.get('/api/site/appearance/')
        self.assertEqual(response.status_code, 200)
        sections = response.json()['sections']
        self.assertTrue(any(s['page'] == 'home' and s['section'] == 'hero' and s['heading'] == 'New EVU Edit' for s in sections))

    def test_disabled_section_is_not_exposed(self):
        SectionAppearance.objects.create(page='home', section='hero', heading='Hidden', enabled=False)
        response = self.client.get('/api/site/appearance/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(any(s['heading'] == 'Hidden' for s in response.json()['sections']))
