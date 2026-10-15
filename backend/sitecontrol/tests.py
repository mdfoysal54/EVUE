from django.test import TestCase
from django.urls import reverse
from .models import SectionAppearance, FeatureFlag

class PublicSiteControlTests(TestCase):
    def test_empty_appearance(self):
        response = self.client.get("/api/site/appearance/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sections"], [])

    def test_section_is_public(self):
        SectionAppearance.objects.create(page="home", section="hero", heading="Welcome")
        response = self.client.get("/api/site/appearance/")
        self.assertEqual(response.json()["sections"][0]["heading"], "Welcome")

    def test_partial_flag_not_exposed_as_enabled(self):
        FeatureFlag.objects.create(key="new-checkout", enabled=True, rollout_percent=50)
        response = self.client.get("/api/site/flags/")
        self.assertFalse(response.json()["flags"]["new-checkout"])
