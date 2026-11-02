from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.utils import timezone
from commerceops.models import OperationsAlert
from commerceops.services import record_alert, resolve_missing_alerts, queue_paid_order_confirmation
from paymentfulfillment.models import PaymentAttempt, Delivery
from variantcommerce.models import Purchase, PurchaseLine, Inventory

class Command(BaseCommand):
    help = "Read-only payment/inventory reconciliation; optionally queue paid-order email notifications."

    def add_arguments(self, parser):
        parser.add_argument("--queue-confirmations", action="store_true")
        parser.add_argument("--limit", type=int, default=10000)

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 100000:
            raise CommandError("--limit must be between 1 and 100000")
        observed = set()
        issues = 0
        purchases = Purchase.objects.select_related("user").order_by("created_at")[:limit]
        for purchase in purchases.iterator(chunk_size=200):
            attempts = PaymentAttempt.objects.filter(purchase=purchase, status=PaymentAttempt.State.VERIFIED)
            verified_count = attempts.count()
            if purchase.status == Purchase.State.PAID and verified_count != 1:
                key = f"reconcile:paid-without-single-verification:{purchase.pk}"
                record_alert(key, OperationsAlert.Severity.CRITICAL, "payment", f"Paid purchase has {verified_count} verified payment attempts")
                observed.add(key); issues += 1
            if purchase.status != Purchase.State.PAID and verified_count:
                key = f"reconcile:verified-not-paid:{purchase.pk}"
                record_alert(key, OperationsAlert.Severity.CRITICAL, "payment", "Verified payment exists for non-paid purchase; investigate before refund/fulfillment")
                observed.add(key); issues += 1
            lines = PurchaseLine.objects.filter(purchase=purchase)
            if purchase.status == Purchase.State.PAID and lines.filter(consumed=False).exists():
                key = f"reconcile:paid-unconsumed:{purchase.pk}"
                record_alert(key, OperationsAlert.Severity.CRITICAL, "inventory", "Paid purchase contains unconsumed reservation lines")
                observed.add(key); issues += 1
            if purchase.status == Purchase.State.PAID and not Delivery.objects.filter(purchase=purchase).exists():
                key = f"reconcile:paid-no-delivery:{purchase.pk}"
                record_alert(key, OperationsAlert.Severity.WARNING, "fulfillment", "Paid purchase has no delivery record")
                observed.add(key); issues += 1
            if options["queue_confirmations"] and purchase.status == Purchase.State.PAID and verified_count == 1:
                queue_paid_order_confirmation(purchase)
        for inventory in Inventory.objects.filter(reserved__gt=0).iterator(chunk_size=200):
            if inventory.reserved > inventory.on_hand:
                key = f"reconcile:overreserved:{inventory.pk}"
                record_alert(key, OperationsAlert.Severity.CRITICAL, "inventory", "Reserved quantity exceeds on-hand quantity")
                observed.add(key); issues += 1
        # Only auto-resolve alerts after a complete scan; limited scans cannot prove resolution.
        total = Purchase.objects.count()
        if total <= limit:
            resolve_missing_alerts("reconcile:", observed)
        self.stdout.write(f"Reconciliation scanned up to {limit} purchases; {issues} issues found. No payments, stock, or orders were changed.")
        if issues:
            raise CommandError("Reconciliation discrepancies found; review Operations Alerts in Django Admin")
