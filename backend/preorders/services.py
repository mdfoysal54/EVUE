from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from .models import Release, PreorderRequest

@transaction.atomic
def reserve_preorder(*, release_id, customer, quantity, idempotency_key):
    if not customer or not customer.is_authenticated:
        raise ValidationError('Sign in to reserve.')
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        raise ValidationError('Quantity must be a positive integer.')
    if not isinstance(idempotency_key, str) or not 8 <= len(idempotency_key) <= 80:
        raise ValidationError('Provide an idempotency key (8-80 characters).')
    # Lock user first to serialize their concurrent requests across releases.
    from django.contrib.auth import get_user_model
    get_user_model().objects.select_for_update().get(pk=customer.pk)
    existing = PreorderRequest.objects.filter(customer=customer, idempotency_key=idempotency_key).first()
    if existing:
        if existing.release_id != int(release_id) or existing.quantity != quantity:
            raise ValidationError('Idempotency key reused for a different request.')
        return existing, False
    release = Release.objects.select_for_update().get(pk=release_id)
    if not release.public or not release.is_open() or not release.product.active:
        raise ValidationError('This pre-order is not available.')
    previous = PreorderRequest.objects.filter(release=release, customer=customer, status=PreorderRequest.Status.RESERVED).aggregate(total=Sum('quantity'))['total'] or 0
    if previous + quantity > release.per_customer_limit:
        raise ValidationError('Customer limit exceeded.')
    if release.reserved + quantity > release.allocation:
        raise ValidationError('Allocation exhausted.')
    release.reserved += quantity
    release.save(update_fields=['reserved', 'updated_at'])
    return PreorderRequest.objects.create(release=release, customer=customer, quantity=quantity, idempotency_key=idempotency_key), True

@transaction.atomic
def cancel_request(*, request_id, customer):
    from django.contrib.auth import get_user_model
    get_user_model().objects.select_for_update().get(pk=customer.pk)
    req = PreorderRequest.objects.select_for_update().get(pk=request_id, customer=customer)
    if req.status != PreorderRequest.Status.RESERVED:
        return req, False
    release = Release.objects.select_for_update().get(pk=req.release_id)
    req.status = PreorderRequest.Status.CANCELLED
    req.save(update_fields=['status'])
    release.reserved -= req.quantity
    release.save(update_fields=['reserved', 'updated_at'])
    return req, True
