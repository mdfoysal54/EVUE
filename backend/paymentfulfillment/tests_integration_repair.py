from unittest.mock import patch
from django.test import TestCase
from django.urls import resolve
from paymentfulfillment import services
from paymentfulfillment.gateway import GatewayError


class PaymentIntegrationRepairTests(TestCase):
    def test_payment_imports_resolve(self):
        self.assertTrue(callable(services.prepare_payment))
        self.assertTrue(callable(services.verify_and_finalize))

    def test_payment_route(self):
        match = resolve("/api/orders/11111111-1111-4111-8111-111111111111/pay/")
        self.assertEqual(match.url_name, "evu-start-payment")

    def test_tracking_route(self):
        match = resolve("/api/orders/11111111-1111-4111-8111-111111111111/tracking/")
        self.assertEqual(match.url_name, "evu-order-tracking")

    @patch("paymentfulfillment.services.validate", side_effect=GatewayError("unavailable"))
    def test_gateway_failure_is_safe(self, _validate):
        with self.assertRaises(services.PaymentError):
            services.verify_and_finalize("test-val")