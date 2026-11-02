import json

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from variantcommerce.models import Purchase

from .services import (
    BusinessRuleError,
    record_courier_event,
    settle_shipping_quote,
    verify_courier_signature,
)

MAX_WEBHOOK_PAYLOAD_SIZE = 65536  # 64 KB


@login_required
@require_POST
def lock_shipping(request):
    try:
        data = json.loads(request.body)
        purchase = Purchase.objects.get(pk=data["purchase_id"], user=request.user)
        quote = settle_shipping_quote(purchase.pk, data["city"])
        return JsonResponse(
            {
                "shipping_fee": str(quote.fee),
                "grand_total": str(quote.grand_total),
                "currency": purchase.currency,
            }
        )
    except (ValueError, KeyError, TypeError, Purchase.DoesNotExist, BusinessRuleError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def courier_webhook(request):
    if len(request.body) > MAX_WEBHOOK_PAYLOAD_SIZE:
        return JsonResponse({"error": "Payload too large"}, status=413)

    signature = request.headers.get("X-EVU-Signature", "")
    if not verify_courier_signature(request.body, signature):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)
        event, created = record_courier_event(
            data["provider"],
            data["shipment_id"],
            data["event_id"],
            data["event_type"],
            data,
        )
        return JsonResponse({"accepted": True, "created": created})
    except (ValueError, KeyError, TypeError, IntegrityError):
        return JsonResponse({"error": "Invalid event"}, status=400)
    except Exception:
        # Never leak internal state or acknowledge unknown shipment as processed.
        return JsonResponse({"error": "Unable to process event"}, status=422)