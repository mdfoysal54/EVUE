import uuid
from django.conf import settings
from django.db import models

class PaymentAttempt(models.Model):
    class State(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        VERIFIED = 'verified', 'Verified'
        FAILED = 'failed', 'Failed'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey('variantcommerce.Purchase', on_delete=models.PROTECT, related_name='payment_attempts')
    transaction_id = models.CharField(max_length=80, unique=True)
    validation_id = models.CharField(max_length=120, blank=True, unique=True, null=True)
    gateway_session = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=12, choices=State.choices, default=State.INITIATED)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

class Delivery(models.Model):
    class State(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PACKING = 'packing', 'Packing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        RETURNED = 'returned', 'Returned'
    purchase = models.OneToOneField('variantcommerce.Purchase', on_delete=models.PROTECT, related_name='delivery')
    recipient = models.CharField(max_length=160)
    phone = models.CharField(max_length=32)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    courier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=State.choices, default=State.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DeliveryEvent(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=12, choices=Delivery.State.choices)
    note = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at', 'id']
