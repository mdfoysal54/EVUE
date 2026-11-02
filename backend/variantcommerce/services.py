from datetime import timedelta
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.db.models import F, Sum
from django.utils import timezone
from .models import Variant, Inventory, VariantCartItem, Purchase, PurchaseLine, PreorderAllocation, VariantPreorder

class CommerceError(Exception): pass

def valid_quantity(q):
    if type(q) is not int or not 1 <= q <= 20: raise CommerceError('Quantity must be an integer from 1 to 20')

@transaction.atomic
def put_cart(user, variant_id, quantity):
    valid_quantity(quantity)
    variant = Variant.objects.select_related('product').filter(pk=variant_id,active=True,product__active=True).first()
    if variant is None: raise CommerceError('Variant unavailable')
    VariantCartItem.objects.update_or_create(user=user,variant=variant,defaults={'quantity':quantity})

def cart_rows(user):
    return list(VariantCartItem.objects.filter(user=user).select_related('variant__product').order_by('variant_id'))

@transaction.atomic
def reserve_checkout(user, key):
    if not isinstance(key,str) or not 8 <= len(key) <= 80: raise CommerceError('Idempotency key required (8-80 chars)')
    prior=Purchase.objects.filter(user=user,idempotency_key=key).first()
    if prior: return prior,False
    cart=cart_rows(user)
    if not cart: raise CommerceError('Cart empty')
    # Lock every inventory row in stable primary-key order to avoid deadlocks.
    variant_ids=[x.variant_id for x in cart]
    rows=list(Inventory.objects.select_for_update().filter(variant_id__in=variant_ids,location__active=True).order_by('pk'))
    by_variant={}
    for row in rows: by_variant.setdefault(row.variant_id,[]).append(row)
    allocations=[]; total=Decimal('0.00'); currency=None
    for item in cart:
        v=item.variant
        valid_quantity(item.quantity)
        if not v.active or not v.product.active: raise CommerceError('Product unavailable')
        if currency is None: currency=v.product.currency
        if currency != v.product.currency: raise CommerceError('Mixed currencies unsupported')
        needed=item.quantity
        for row in by_variant.get(v.id,[]):
            take=min(needed,row.on_hand-row.reserved)
            if take:
                allocations.append((item,row,take)); needed-=take
            if not needed: break
        if needed: raise CommerceError(f'Insufficient stock for {v.sku}')
        total+=v.price*item.quantity
    try:
        # A duplicate key from a concurrent request must not allocate stock twice.
        with transaction.atomic():
            purchase=Purchase.objects.create(user=user,idempotency_key=key,total=total,currency=currency,expires_at=timezone.now()+timedelta(minutes=15))
    except IntegrityError:
        return Purchase.objects.get(user=user,idempotency_key=key),False
    for item,row,qty in allocations:
        Inventory.objects.filter(pk=row.pk).update(reserved=F('reserved')+qty)
        PurchaseLine.objects.create(purchase=purchase,variant=item.variant,inventory=row,quantity=qty,unit_price=item.variant.price)
    VariantCartItem.objects.filter(user=user).delete()
    return purchase,True

@transaction.atomic
def cancel_purchase(user,purchase_id):
    purchase=Purchase.objects.select_for_update().get(pk=purchase_id,user=user)
    if purchase.status == Purchase.State.CANCELLED: return purchase
    if purchase.status != Purchase.State.RESERVED: raise CommerceError('Cannot cancel this purchase')
    lines=list(PurchaseLine.objects.select_for_update().filter(purchase=purchase,released=False,consumed=False).order_by('pk'))
    for line in lines:
        Inventory.objects.filter(pk=line.inventory_id).update(reserved=F('reserved')-line.quantity)
        line.released=True;line.save(update_fields=['released'])
    purchase.status=Purchase.State.CANCELLED;purchase.save(update_fields=['status'])
    return purchase

@transaction.atomic
def reserve_preorder(user,allocation_id,quantity,key):
    valid_quantity(quantity)
    if not isinstance(key,str) or not 8 <= len(key) <= 80: raise CommerceError('Idempotency key required (8-80 chars)')
    existing=VariantPreorder.objects.filter(user=user,idempotency_key=key).first()
    if existing: return existing,False
    allocation=PreorderAllocation.objects.select_for_update().select_related('release','variant__product').get(pk=allocation_id)
    release=allocation.release
    if not release.public or not release.is_open() or not allocation.variant.active or not allocation.variant.product.active or allocation.variant.product_id != release.product_id:
        raise CommerceError('Pre-order not available')
    current=VariantPreorder.objects.filter(user=user,allocation__release=release,status=VariantPreorder.State.RESERVED).aggregate(total=Sum('quantity'))['total'] or 0
    if current+quantity>release.per_customer_limit: raise CommerceError('Customer limit exceeded')
    if allocation.reserved+quantity>allocation.capacity: raise CommerceError('Allocation exhausted')
    try:
        with transaction.atomic():
            item=VariantPreorder.objects.create(user=user,allocation=allocation,quantity=quantity,idempotency_key=key)
    except IntegrityError:
        return VariantPreorder.objects.get(user=user,idempotency_key=key),False
    PreorderAllocation.objects.filter(pk=allocation.pk).update(reserved=F('reserved')+quantity)
    return item,True

@transaction.atomic
def cancel_preorder(user,item_id):
    item=VariantPreorder.objects.select_for_update().get(pk=item_id,user=user)
    if item.status == VariantPreorder.State.CANCELLED: return item
    allocation=PreorderAllocation.objects.select_for_update().get(pk=item.allocation_id)
    PreorderAllocation.objects.filter(pk=allocation.pk).update(reserved=F('reserved')-item.quantity)
    item.status=VariantPreorder.State.CANCELLED;item.save(update_fields=['status'])
    return item
