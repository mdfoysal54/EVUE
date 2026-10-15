from django.conf import settings
from django.db import models

class CustomerProfile(models.Model):
    class Verification(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending", "Pending review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    verification_status = models.CharField(max_length=16, choices=Verification.choices, default=Verification.UNVERIFIED)
    verification_note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user_id}"