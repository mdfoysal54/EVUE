"""Read-only EVU staging commerce audit. Exit nonzero for integrity problems."""
import json
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.utils import timezone

# Adjust model imports to match your project's app layout
from .models import (
    Delivery,
    Inventory,
    PaymentAttempt,
    PreorderAllocation,
    Purchase,
    PurchaseLine,
    RefundCase,
    ShippingQuote,
)


class Command(BaseCommand):
    help = "Audit commerce integrity in staging (read-only); --json for machine-readable results."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", dest="as_json")
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Treat operational warnings as failures",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        errors = {}
        warnings = {}

        # Critical integrity checks
        errors["inventory_over_reserved"] = Inventory.objects.filter(
            reserved__gt=F("on_hand")
        ).count()

        errors["preorder_over_allocated"] = PreorderAllocation.objects.filter(
            reserved__gt=F("capacity")
        ).count()

        errors["paid_without_verified_payment"] = (
            Purchase.objects.filter(status=Purchase.State.PAID)
            .exclude(payment_attempts__status=PaymentAttempt.State.VERIFIED)
            .distinct()
            .count()
        )

        errors["verified_payment_unpaid_purchase"] = (
            PaymentAttempt.objects.filter(status=PaymentAttempt.State.VERIFIED)
            .exclude(purchase__status=Purchase.State.PAID)
            .count()
        )

        errors["verified_amount_mismatch"] = (
            PaymentAttempt.objects.filter(status=PaymentAttempt.State.VERIFIED)
            .exclude(
                amount=F("purchase__total"),
                currency=F("purchase__currency"),
            )
            .count()
        )

        errors["shipping_total_mismatch"] = ShippingQuote.objects.exclude(
            grand_total=F("merchandise_total") + F("fee")
        ).count()

        errors["shipping_purchase_total_mismatch"] = ShippingQuote.objects.exclude(
            grand_total=F("purchase__total")
        ).count()

        errors["paid_lines_not_consumed"] = (
            PurchaseLine.objects.filter(purchase__status=Purchase.State.PAID)
            .filter(Q(consumed=False) | Q(released=True))
            .count()
        )

        errors["active_reservations_without_stock"] = (
            PurchaseLine.objects.filter(purchase__status=Purchase.State.RESERVED)
            .filter(Q(consumed=True) | Q(released=True))
            .count()
        )

        errors["settled_refunds_missing_gateway_reference"] = RefundCase.objects.filter(
            state=RefundCase.State.SETTLED,
            gateway_reference="",
        ).count()

        # Operational warnings
        warnings["expired_reservations_awaiting_cleanup"] = Purchase.objects.filter(
            status=Purchase.State.RESERVED,
            expires_at__lt=now,
        ).count()

        warnings["paid_orders_without_delivery"] = Purchase.objects.filter(
            status=Purchase.State.PAID,
            delivery__isnull=True,
        ).count()

        warnings["approved_refunds_awaiting_gateway"] = RefundCase.objects.filter(
            state=RefundCase.State.APPROVED
        ).count()

        warnings["shipped_without_tracking"] = Delivery.objects.filter(
            status=Delivery.State.SHIPPED,
            tracking_number="",
        ).count()

        is_failed = any(errors.values()) or (options["strict"] and any(warnings.values()))
        result = {
            "checked_at": now.isoformat(),
            "errors": errors,
            "warnings": warnings,
            "status": "FAIL" if is_failed else "PASS",
        }

        if options["as_json"]:
            self.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        else:
            self.stdout.write(f"EVU STAGING AUDIT: {result['status']}")
            for kind in ("errors", "warnings"):
                for name, count in result[kind].items():
                    self.stdout.write(f"{kind.upper()} {name}: {count}")

        if result["status"] == "FAIL":
            raise CommandError("Commerce integrity audit failed; investigate before launch")