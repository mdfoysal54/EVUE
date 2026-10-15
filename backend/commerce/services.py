from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import CartItem, Order, OrderItem, Reservation, Stock

class CheckoutError(Exception):
    pass

@transaction.atomic
def create_order(user):
    items = list(CartItem.objects.filter(user=user).select_related("product").order_by("product_id"))
    if not items:
        raise CheckoutError("Cart is empty")
    ids = [item.product_id for item in items]
    stocks = {s.product_id: s for s in Stock.objects.select_for_update().filter(product_id__in=ids).order_by("product_id")}
    currency = items[0].product.currency
    total = Decimal("0.00")
    for item in items:
        p = item.product
        if not p.active or p.currency != currency or item.quantity < 1 or item.quantity > 20:
            raise CheckoutError("Invalid product, currency or quantity")
        s = stocks.get(p.pk)
        if not s or s.on_hand - s.reserved < item.quantity:
            raise CheckoutError("Insufficient stock")
        total += p.price * item.quantity
    order = Order.objects.create(user=user, currency=currency, total=total, expires_at=timezone.now()+timedelta(minutes=15))
    for item in items:
        p = item.product
        OrderItem.objects.create(order=order, product=p, name=p.name, unit_price=p.price, quantity=item.quantity)
        stock = stocks[p.pk]
        Stock.objects.filter(pk=stock.pk).update(reserved=F("reserved")+item.quantity)
        Reservation.objects.create(order=order, stock=stock, quantity=item.quantity)
    CartItem.objects.filter(user=user).delete()
    return order

@transaction.atomic
def cancel_order(user, order_id):
    order = Order.objects.select_for_update().get(pk=order_id, user=user)
    if order.status != Order.Status.PENDING:
        raise CheckoutError("Order cannot be cancelled")
    for reservation in Reservation.objects.select_for_update().filter(order=order, released=False, consumed=False).order_by("stock_id"):
        Stock.objects.filter(pk=reservation.stock_id).update(reserved=F("reserved")-reservation.quantity)
        reservation.released = True
        reservation.save(update_fields=["released"])
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return order

@transaction.atomic
def release_expired():
    count = 0
    ids = list(Order.objects.filter(status=Order.Status.PENDING, expires_at__lte=timezone.now()).values_list("pk",flat=True))
    for oid in ids:
        order = Order.objects.select_for_update().get(pk=oid)
        if order.status != Order.Status.PENDING or order.expires_at > timezone.now():
            continue
        for reservation in Reservation.objects.select_for_update().filter(order=order, released=False, consumed=False).order_by("stock_id"):
            Stock.objects.filter(pk=reservation.stock_id).update(reserved=F("reserved")-reservation.quantity)
            reservation.released = True
            reservation.save(update_fields=["released"])
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        count += 1
    return count
