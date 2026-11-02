from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from commerceops.models import NotificationOutbox

class Command(BaseCommand):
    help = "Send queued transactional email messages using configured Django email backend."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1 or limit > 500:
            raise CommandError("--limit must be 1..500")
        if not options["dry_run"] and not getattr(settings, "DEFAULT_FROM_EMAIL", ""):
            raise CommandError("DEFAULT_FROM_EMAIL must be configured")
        ids = list(NotificationOutbox.objects.filter(status=NotificationOutbox.Status.PENDING)
                   .order_by("created_at").values_list("pk", flat=True)[:limit])
        if options["dry_run"]:
            self.stdout.write(f"{len(ids)} pending emails; none sent")
            return
        sent = 0
        for pk in ids:
            # Claim row before sending so parallel workers do not process it simultaneously.
            with transaction.atomic():
                row = NotificationOutbox.objects.select_for_update().get(pk=pk)
                if row.status != NotificationOutbox.Status.PENDING:
                    continue
                row.status = NotificationOutbox.Status.FAILED
                row.attempts += 1
                row.save(update_fields=["status", "attempts"])
            try:
                send_mail(row.subject, row.body, settings.DEFAULT_FROM_EMAIL, [row.recipient_email], fail_silently=False)
            except Exception as exc:
                NotificationOutbox.objects.filter(pk=pk).update(last_error=str(exc)[:500])
                self.stderr.write(f"Email failed for outbox id {pk}")
            else:
                NotificationOutbox.objects.filter(pk=pk).update(status=NotificationOutbox.Status.SENT, sent_at=timezone.now(), last_error="")
                sent += 1
        self.stdout.write(f"Sent {sent} messages. Failed messages require operator review before retry to avoid duplicate delivery.")
