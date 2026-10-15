from django.core.management.base import BaseCommand
from commerce.services import release_expired
class Command(BaseCommand):
    help = "Release expired unpaid order reservations (run periodically)"
    def handle(self, *args, **kwargs):
        self.stdout.write(f"Released {release_expired()} expired orders")