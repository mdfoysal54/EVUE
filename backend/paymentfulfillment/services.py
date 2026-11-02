import uuid
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from variantcommerce.models import Purchase, PurchaseLine, Inventory
from .models import PaymentAttempt, Delivery, DeliveryEvent
from .gateway import GatewayError, validate, config

class PaymentError(Exception):
    pass

@transaction.atomic
def prepare_payment(user, purchase_id, address):
    purchase = Purchase.objects.select_for_update().get(pk=purchase_id, user=user)
    if purchase.status != Purchase.State.RESERVED or purchase.expires_at <= timezone.now():
        raise PaymentError('Order is not available for payment')
    required = ('recipient', 'phone', 'address', 'city')
    if any(not isinstance(address.get(k), str) or not address[k].strip() for k in required):
        raise PaymentError('Recipient, phone, address and city are required')
    if any(len(address[k]) > maxlen for k, maxlen in [('recipient',160),('phone',32),('address',1000),('city',100)]):
        raise PaymentError('Delivery details are too long')
    delivery, _ = Delivery.objects.get_or_create(purchase=purchase, defaults={k: address[k].strip() for k in required})
    existing = PaymentAttempt.objects.filter(purchase=purchase, status=PaymentAttempt.State.INITIATED).order_by('-created_at').first()
    if existing and existing.gateway_session:
        raise PaymentError('A payment session already exists; retry from the payment page or contact support')
    attempt = PaymentAttempt.objects.create(purchase=purchase, transaction_id='EVU-' + uuid.uuid4().hex, amount=purchase.total, currency=purchase.currency)
    return attempt, delivery

@transaction.atomic
def verify_and_finalize(validation_id):
    # Validation is performed against the gateway; callback fields are never treated as proof of payment.
    result = validate(validation_id)
    store_id, _, _ = config()
    if result.get('store_id') and str(result['store_id']) != str(store_id):
        raise PaymentError('Gateway merchant identity mismatch')
    tran_id = result.get('tran_id')
    if not tran_id:
        raise PaymentError('Gateway did not return a transaction ID')
    attempt = PaymentAttempt.objects.select_for_update().select_related('purchase').filter(transaction_id=tran_id).first()
    if attempt is None:
        raise PaymentError('Unknown payment transaction')
    purchase = Purchase.objects.select_for_update().get(pk=attempt.purchase_id)
    try:
        paid = Decimal(str(result.get('amount', '')))
    except (InvalidOperation, ValueError):
        raise PaymentError('Invalid gateway amount')
    if (result.get('currency') != attempt.currency or paid != attempt.amount
            or attempt.amount != purchase.total or attempt.currency != purchase.currency):
        raise PaymentError('Gateway payment details do not match order')
    if attempt.status == PaymentAttempt.State.VERIFIED:
        if attempt.validation_id != validation_id:
            raise PaymentError('Conflicting validation ID')
        return purchase
    if PaymentAttempt.objects.filter(validation_id=validation_id).exclude(pk=attempt.pk).exists():
        raise PaymentError('Validation ID already used')
    if purchase.status != Purchase.State.RESERVED or purchase.expires_at <= timezone.now():
        # Do not mark a late payment fulfilled: reconcile and refund manually.
        raise PaymentError('Payment received for an expired/cancelled order: manual refund review required')
    lines = list(PurchaseLine.objects.select_for_update().filter(purchase=purchase).order_by('pk'))
    if not lines or any(line.released or line.consumed for line in lines):
        raise PaymentError('Reservation is no longer valid')
    for line in lines:
        updated = Inventory.objects.filter(pk=line.inventory_id, reserved__gte=line.quantity, on_hand__gte=line.quantity).update(
            reserved=F('reserved')-line.quantity, on_hand=F('on_hand')-line.quantity)
        if updated != 1:
            raise PaymentError('Stock reconciliation failed; manual review required')
        line.consumed = True
        line.save(update_fields=['consumed'])
    purchase.status = Purchase.State.PAID
    purchase.save(update_fields=['status'])
    attempt.status = PaymentAttempt.State.VERIFIED
    attempt.validation_id = validation_id
    attempt.verified_at = timezone.now()
    attempt.save(update_fields=['status', 'validation_id', 'verified_at'])
    delivery, _ = Delivery.objects.get_or_create(purchase=purchase, defaults={
        'recipient': purchase.user.get_username(), 'phone': 'Not provided', 'address': 'Address pending', 'city': 'Unknown'})
    DeliveryEvent.objects.get_or_create(delivery=delivery, status=Delivery.State.PENDING, note='Payment verified')
    return purchase
