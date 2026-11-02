import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class Release(models.Model):
    class State(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PREVIEW = 'preview', 'Preview'
        PREORDER = 'preorder', 'Pre-order open'
        CLOSED = 'closed', 'Closed'
        CANCELLED = 'cancelled', 'Cancelled'
    product = models.OneToOneField('catalog.Product', on_delete=models.PROTECT, related_name='preorder_release')
    state = models.CharField(max_length=12, choices=State.choices, default=State.DRAFT)
    reveal_at = models.DateTimeField()
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    expected_ship_start = models.DateField()
    expected_ship_end = models.DateField()
    allocation = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    per_customer_limit = models.PositiveSmallIntegerField(default=2)
    public = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.reveal_at > self.opens_at or self.opens_at >= self.closes_at:
            raise ValidationError('Require reveal_at <= opens_at < closes_at.')
        if self.expected_ship_start > self.expected_ship_end:
            raise ValidationError('Expected shipping dates are reversed.')
        if self.reserved > self.allocation:
            raise ValidationError('Reserved quantity cannot exceed allocation.')
        if self.per_customer_limit < 1:
            raise ValidationError('Per-customer limit must be positive.')

    def is_open(self):
        now = timezone.now()
        return self.state == self.State.PREORDER and self.opens_at <= now < self.closes_at

    def __str__(self):
        return f'{self.product} ({self.state})'

class PreorderRequest(models.Model):
    class Status(models.TextChoices):
        RESERVED = 'reserved', 'Reserved (not paid)'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'
        CONVERTED = 'converted', 'Converted to order'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    release = models.ForeignKey(Release, on_delete=models.PROTECT, related_name='requests')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RESERVED)
    idempotency_key = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['customer', 'idempotency_key'], name='preorder_customer_idempotency')]
    def __str__(self):
        return f'{self.customer_id} / {self.release_id} / {self.status}'

class WaitlistEntry(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name='waitlist')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['release', 'customer'], name='preorder_unique_waitlist_customer')]
