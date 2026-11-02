import hashlib
import hmac

from django.test import SimpleTestCase, override_settings

from .services import verify_courier_signature


class SignatureTests(SimpleTestCase):
    @override_settings(EVU_COURIER_WEBHOOK_SECRET="test-only")
    def test_valid_and_invalid(self):
        body = b'{"event":"delivered"}'
        sig = hmac.new(b"test-only", body, hashlib.sha256).hexdigest()

        self.assertTrue(verify_courier_signature(body, sig))
        self.assertFalse(verify_courier_signature(body + b"!", sig))

    @override_settings(EVU_COURIER_WEBHOOK_SECRET="")
    def test_missing_secret_fails_closed(self):
        self.assertFalse(verify_courier_signature(b"{}", "anything"))