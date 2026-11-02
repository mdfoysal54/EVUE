from django.conf import settings
from django.db import models

class WishlistItem(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="wishlist_entries")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["customer", "product"], name="unique_wishlist_customer_product")]
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return f"{self.customer_id}: {self.product_id}"
