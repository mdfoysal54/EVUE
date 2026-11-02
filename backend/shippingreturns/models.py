from django.conf import settings
from django.db import models
from django.db.models import Q

class ShippingZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, unique=True, help_text="Exact city match, case-insensitive")
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city} — BDT {self.fee}"

class ReturnRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        REVIEWING = "reviewing", "Reviewing"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        RECEIVED = "received", "Received"
        CLOSED = "closed", "Closed"

    purchase = models.ForeignKey("variantcommerce.Purchase", on_delete=models.PROTECT, related_name="return_requests")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField(max_length=2000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    staff_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["purchase", "user"], name="evu_unique_return_per_order_customer")]