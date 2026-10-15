from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Announcement(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    published = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Offer(models.Model):
    code = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=250)
    percent_off = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    active = models.BooleanField(default=False)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError('Offer end must be after start')
    def __str__(self): return self.code

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evu_notifications')
    title = models.CharField(max_length=160)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class TransactionRecord(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    reference = models.CharField(max_length=120, unique=True)
    provider = models.CharField(max_length=50)
    amount_minor = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=12, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.reference

class AdminAuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    target = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self): return self.action