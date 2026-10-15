import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from catalog.models import Product

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.PROTECT, related_name="inventory")
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.product.name}: {self.on_hand} / reserved {self.reserved}"

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evu_cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="evu_unique_cart_item")]

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Awaiting payment"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="evu_orders")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    currency = models.CharField(max_length=3)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    class Meta:
        ordering = ["-created_at"]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

class Reservation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservations")
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    consumed = models.BooleanField(default=False)
    released = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["order", "stock"], name="evu_unique_order_stock")]
