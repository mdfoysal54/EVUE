from django.core.management.base import BaseCommand
from django.db.models import F

from commercecontrol.models import RefundCase, ShippingQuote
from paymentfulfillment.models import PaymentAttempt
from variantcommerce.models import Inventory, Purchase


class Command(BaseCommand):
    help = "Read-only launch checks for inventory, shipping, and payments"

    def handle(self, *args, **options):
        checks = {
            "negative_available_inventory": Inventory.objects.filter(
                reserved__gt=F("on_hand")
            ).count(),
            "paid_without_verified_payment": Purchase.objects.filter(
                status="paid"
            )
            .exclude(payment_attempts__status="verified")
            .distinct()
            .count(),
            "payment_started_without_shipping_quote": PaymentAttempt.objects.filter(
                purchase__shipping_quotes__isnull=True
            ).count(),
            "refunds_awaiting_submission": RefundCase.objects.filter(
                state="approved"
            ).count(),
        }

        for name, count in checks.items():
            self.stdout.write(f"{name}: {count}")

        if any(checks.values()):
            self.stderr.write(
                "Review outstanding issues before enabling live commerce."
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("All launch verification checks passed.")
            )