from django.utils import timezone
from .models import OperationsAlert, NotificationOutbox


def record_alert(key, severity, category, detail):
    alert, _ = OperationsAlert.objects.update_or_create(
        key=key,
        defaults={"severity": severity, "category": category, "detail": detail,
                  "active": True, "resolved_at": None},
    )
    return alert


def resolve_missing_alerts(prefix, observed):
    OperationsAlert.objects.filter(key__startswith=prefix, active=True).exclude(
        key__in=observed
    ).update(active=False, resolved_at=timezone.now())


def queue_paid_order_confirmation(purchase):
    email = (purchase.user.email or "").strip()
    if not email:
        return None
    event_key = f"order-paid:{purchase.pk}"
    notification, _ = NotificationOutbox.objects.get_or_create(
        event_key=event_key,
        defaults={
            "recipient_email": email,
            "subject": "Your EVU order is confirmed",
            "body": f"Your payment was verified and order {purchase.pk} is confirmed. You can view tracking in your EVU account.",
        },
    )
    return notification
