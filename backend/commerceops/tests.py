from django.test import SimpleTestCase
from django.core.management import call_command
from io import StringIO

class OpsCommandsSmokeTests(SimpleTestCase):
    def test_reconciliation_rejects_invalid_limit(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("reconcile_evu_orders", limit=0, stdout=StringIO())

    def test_notification_rejects_invalid_limit(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("send_evu_notifications", limit=0, stdout=StringIO())
