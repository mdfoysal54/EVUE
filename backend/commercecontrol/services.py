import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from commercecontrol.models import (
    AuditEvent,
    CourierEvent,
    CourierShipment,
    RefundCase,
    ShippingQuote,
)
from commerceops.models import NotificationOutbox
from paymentfulfillment.models import Delivery, DeliveryEvent
from shippingreturns.models import ShippingZone
from variantcommerce.models import Purchase, PurchaseLine


class BusinessRuleError(ValueError):
    """Raised when a commerce or fulfillment business invariant is violated."""
    pass


@transaction.atomic
def settle_shipping_quote(purchase_id, city: str) -> ShippingQuote:
    """
    Locks the order and snapshots the authoritative shipping fee before payment initiation.
    """
    purchase = Purchase.objects.select_for_update().get(pk=purchase_id)

    if purchase.status != Purchase.State.RESERVED or purchase.expires_at <= timezone.now():
        raise BusinessRuleError('Only active unpaid reservations can be quoted')

    if purchase.payment_attempts.exists():
        raise BusinessRuleError('Payment attempt exists; shipping cannot be changed')

    if ShippingQuote.objects.filter(purchase=purchase).exists():
        raise BusinessRuleError('Quote already locked; cancel and restart checkout to change shipping')

    zone = ShippingZone.objects.filter(city__iexact=city.strip(), active=True).first()
    if not zone:
        raise BusinessRuleError('No active shipping zone for this city')

    lines = PurchaseLine.objects.filter(purchase=purchase)
    subtotal = sum((line.unit_price * line.quantity for line in lines), Decimal('0.00'))
    if subtotal != purchase.total:
        raise BusinessRuleError('Order subtotal mismatch; manual review required')

    fee = zone.fee
    if fee < Decimal('0.00'):
        raise BusinessRuleError('Invalid shipping fee')

    grand_total = subtotal + fee
    quote = ShippingQuote.objects.create(
        purchase=purchase,
        zone=zone,
        city_snapshot=zone.city,
        fee=fee,
        merchandise_total=subtotal,
        grand_total=grand_total,
    )

    purchase.total = grand_total
    purchase.save(update_fields=['total'])
    return quote


@transaction.atomic
def approve_refund(case_id, actor) -> RefundCase:
    if not actor.is_active or not actor.has_perm('commercecontrol.change_refundcase'):
        raise PermissionError('Refund approval permission required')

    case = RefundCase.objects.select_for_update().select_related('purchase').get(pk=case_id)

    if case.state != RefundCase.State.REQUESTED or case.amount <= Decimal('0.00'):
        raise BusinessRuleError('Invalid refund state or amount')

    if case.purchase.status != Purchase.State.PAID:
        raise BusinessRuleError('Only paid orders can be refunded')

    verified = case.purchase.payment_attempts.filter(status='verified').first()
    if not verified:
        raise BusinessRuleError('No verified payment')

    other_refunds = (
        RefundCase.objects.filter(
            purchase=case.purchase,
            state__in=[
                RefundCase.State.APPROVED,
                RefundCase.State.SUBMITTED,
                RefundCase.State.SETTLED,
            ],
        )
        .exclude(pk=case.pk)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    if case.amount + other_refunds > verified.amount:
        raise BusinessRuleError('Refund amount exceeds verified payment')

    case.state = RefundCase.State.APPROVED
    case.approved_by = actor
    case.save(update_fields=['state', 'approved_by', 'updated_at'])

    AuditEvent.objects.create(
        actor=actor,
        action='refund.approved',
        object_ref=str(case.pk),
        details={'amount': str(case.amount)},
    )
    return case


@transaction.atomic
def record_gateway_refund(case_id, gateway_reference: str, gateway_response: dict, actor) -> RefundCase:
    """
    Record VERIFIED gateway settlement only; do not call this on initial submission.
    """
    if not actor.is_active or not actor.has_perm('commercecontrol.change_refundcase'):
        raise PermissionError('Refund reconciliation permission required')

    case = RefundCase.objects.select_for_update().get(pk=case_id)

    if case.state != RefundCase.State.SUBMITTED or not gateway_reference:
        raise BusinessRuleError('Gateway submission and reference required')

    if gateway_response.get('verified_settled') is not True:
        raise BusinessRuleError('Independently verified gateway settlement required')

    case.state = RefundCase.State.SETTLED
    case.gateway_reference = gateway_reference
    case.gateway_response = gateway_response
    case.save(update_fields=['state', 'gateway_reference', 'gateway_response', 'updated_at'])

    AuditEvent.objects.create(
        actor=actor,
        action='refund.settled',
        object_ref=str(case.pk),
        details={'gateway_reference': gateway_reference},
    )
    return case


@transaction.atomic
def record_courier_event(provider: str, external_id: str, event_id: str, event_type: str, payload: dict):
    shipment = CourierShipment.objects.select_for_update().get(
        provider=provider,
        external_id=external_id,
    )

    event, created = CourierEvent.objects.get_or_create(
        shipment=shipment,
        external_event_id=event_id,
        defaults={'event_type': event_type, 'payload': payload},
    )
    if not created:
        return event, False

    status_map = {
        'picked_up': Delivery.State.SHIPPED,
        'in_transit': Delivery.State.SHIPPED,
        'delivered': Delivery.State.DELIVERED,
        'returned': Delivery.State.RETURNED,
    }
    new_status = status_map.get(event_type)

    delivery = Delivery.objects.select_for_update().select_related('purchase__user').get(pk=shipment.delivery_id)

    # State machine transition rules: terminal statuses cannot be overwritten
    allowed_transitions = {
        Delivery.State.PACKING: {Delivery.State.SHIPPED},
        Delivery.State.SHIPPED: {Delivery.State.DELIVERED, Delivery.State.RETURNED},
    }

    if (
        new_status
        and new_status != delivery.status
        and new_status in allowed_transitions.get(delivery.status, set())
    ):
        delivery.status = new_status
        delivery.save(update_fields=['status', 'updated_at'])

        DeliveryEvent.objects.create(
            delivery=delivery,
            status=new_status,
            note=f'Courier: {event_type}'[:250],
        )

        email = getattr(delivery.purchase.user, 'email', None)
        if email:
            NotificationOutbox.objects.get_or_create(
                event_key=f'courier:{shipment.pk}:{event_id}',
                defaults={
                    'recipient_email': email,
                    'subject': f'EVU order {new_status}',
                    'body': f'Your order {delivery.purchase_id} is now {new_status}.',
                },
            )

    shipment.last_event_id = event_id
    shipment.save(update_fields=['last_event_id', 'updated_at'])
    return event, True


def verify_courier_signature(raw_body: bytes, signature: str) -> bool:
    secret = getattr(settings, 'EVU_COURIER_WEBHOOK_SECRET', '')
    if not secret or not signature:
        return False

    digest = hmac.new(
        secret.encode('utf-8'),
        raw_body if isinstance(raw_body, bytes) else raw_body.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(digest, signature)