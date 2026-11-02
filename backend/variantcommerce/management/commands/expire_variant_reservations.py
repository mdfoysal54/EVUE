from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from variantcommerce.models import Purchase,PurchaseLine,Inventory

class Command(BaseCommand):
    help = "Release expired, unpaid variant checkout reservations. Safe to rerun."
    def add_arguments(self, parser):
        parser.add_argument("--limit",type=int,default=100)
    def handle(self,*args,**options):
        limit=options["limit"]
        if not 1 <= limit <= 1000: raise ValueError("limit must be 1..1000")
        expired=0
        ids=list(Purchase.objects.filter(status=Purchase.State.RESERVED,expires_at__lte=timezone.now()).order_by("expires_at").values_list("pk",flat=True)[:limit])
        for pk in ids:
            with transaction.atomic():
                purchase=Purchase.objects.select_for_update().get(pk=pk)
                if purchase.status!=Purchase.State.RESERVED or purchase.expires_at>timezone.now(): continue
                lines=list(PurchaseLine.objects.select_for_update().filter(purchase=purchase,released=False,consumed=False).order_by("pk"))
                for line in lines:
                    stock=Inventory.objects.select_for_update().get(pk=line.inventory_id)
                    if stock.reserved<line.quantity: raise RuntimeError(f"Reservation ledger mismatch: inventory {stock.pk}")
                    Inventory.objects.filter(pk=stock.pk).update(reserved=F("reserved")-line.quantity)
                    line.released=True
                    line.save(update_fields=["released"])
                purchase.status=Purchase.State.EXPIRED
                purchase.save(update_fields=["status"])
                expired+=1
        self.stdout.write(self.style.SUCCESS(f"Expired reservations: {expired}"))
