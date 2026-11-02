import uuid
from django.conf import settings
from django.db import models


class ShippingQuote(models.Model):
    purchase = models.OneToOneField(
        'variantcommerce.Purchase',
        on_delete=models.PROTECT,
        related_name='shipping_quote',
    )
    zone = models.ForeignKey(
        'shippingreturns.ShippingZone',
        on_delete=models.PROTECT,
        related_name='shipping_quotes',
    )
    city_snapshot = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    merchandise_total = models.DecimalField(max_digits=14, decimal_places=2)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote for Purchase {self.purchase_id} - {self.grand_total}"


class RefundCase(models.Model):
    class State(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        APPROVED = 'approved', 'Approved'
        SUBMITTED = 'submitted', 'Submitted to gateway'
        SETTLED = 'settled', 'Settled by gateway'
        REJECTED = 'rejected', 'Rejected'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey(
        'variantcommerce.Purchase',
        on_delete=models.PROTECT,
        related_name='refund_cases',
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    reason = models.TextField(max_length=1000)
    state = models.CharField(
        max_length=16,
        choices=State.choices,
        default=State.REQUESTED,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='approved_refunds',
    )
    gateway_reference = models.CharField(max_length=150, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.id} ({self.get_state_display()})"


class CourierShipment(models.Model):
    delivery = models.OneToOneField(
        'paymentfulfillment.Delivery',
        on_delete=models.PROTECT,
        related_name='courier_shipment',
    )
    provider = models.CharField(max_length=40)
    external_id = models.CharField(max_length=120)
    tracking_number = models.CharField(max_length=120)
    last_event_id = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'external_id'],
                name='cc_provider_external_unique',
            )
        ]

    def __str__(self):
        return f"{self.provider}: {self.tracking_number}"


class CourierEvent(models.Model):
    shipment = models.ForeignKey(
        CourierShipment,
        on_delete=models.PROTECT,
        related_name='provider_events',
    )
    external_event_id = models.CharField(max_length=120)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']
        constraints = [
            models.UniqueConstraint(
                fields=['shipment', 'external_event_id'],
                name='cc_courier_event_unique',
            )
        ]

    def __str__(self):
        return f"{self.shipment_id} - {self.event_type} ({self.external_event_id})"


class VIPProfile(models.Model):
    class Tier(models.TextChoices):
        STANDARD = 'standard', 'Standard'
        SILVER = 'silver', 'Silver'
        GOLD = 'gold', 'Gold'
        PRIVATE = 'private', 'Private'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evu_vip',
    )
    tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        default=Tier.STANDARD,
    )
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='advised_clients',
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.get_tier_display()}"


class PrivateAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='private_accesses',
    )
    release = models.ForeignKey(
        'preorders.Release',
        on_delete=models.PROTECT,
        related_name='private_grants',
    )
    expires_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'release'],
                name='cc_private_release_unique',
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.release_id} (Expires: {self.expires_at})"


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_events',
    )
    action = models.CharField(max_length=100)
    object_ref = models.CharField(max_length=180)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.object_ref}"