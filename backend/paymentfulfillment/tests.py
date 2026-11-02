from unittest.mock import patch
from django.test import TestCase
from .services import PaymentError, verify_and_finalize

# Integration test requires the project's catalog Category/Product fixtures to be configured.
# A narrow verification test checks rejection of unknown gateway transactions without fixtures.
class GatewayVerificationTests(TestCase):
    @patch("paymentfulfillment.services.config")
    @patch("paymentfulfillment.services.validate")
    def test_unknown_transaction_never_marks_paid(self, mock_validate, mock_config):
        mock_validate.return_value = {
            "status": "VALID",
            "tran_id": "UNKNOWN",
            "amount": "1.00",
            "currency": "BDT",
        }
        mock_config.return_value = ("sandbox-store", "test-only-password", True)

        with self.assertRaises(PaymentError):
            verify_and_finalize("valid-id")