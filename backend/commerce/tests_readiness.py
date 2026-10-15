from django.core.management import call_command
from django.test import TestCase
from io import StringIO

class CommerceReadinessTest(TestCase):
    def test_readiness_command(self):
        out = StringIO()
        call_command("check_commerce_readiness", stdout=out)
        self.assertIn("All registered application model tables exist", out.getvalue())