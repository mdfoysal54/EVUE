import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F

class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='sku_variants')
    sku = models.CharField(max_length=80, unique=True)
    size = models.CharField(max_length=32, blank=True)
    color = models.CharField(max_length=60, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['product','size','color'],name='vc_unique_product_options')]
    def __str__(self): return self.sku

class Location(models.Model):
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Inventory(models.Model):
    variant = models.ForeignKey(Variant,on_delete=models.PROTECT,related_name='inventory_rows')
    location = models.ForeignKey(Location,on_delete=models.PROTECT)
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['variant','location'],name='vc_unique_stock_location'),models.CheckConstraint(condition=Q(reserved__lte=F('on_hand')),name='vc_reserved_not_over_hand')]
    def __str__(self): return f'{self.variant.sku}@{self.location.code}'

class VariantCartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant,on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','variant'],name='vc_unique_cart_variant')]

class Purchase(models.Model):
    class State(models.TextChoices):
        RESERVED='reserved','Awaiting payment'
        PAID='paid','Paid'
        CANCELLED='cancelled','Cancelled'
        EXPIRED='expired','Expired'
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    status = models.CharField(max_length=12,choices=State.choices,default=State.RESERVED)
    currency = models.CharField(max_length=3,default='BDT')
    total = models.DecimalField(max_digits=14,decimal_places=2)
    idempotency_key = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','idempotency_key'],name='vc_unique_checkout_key')]

class PurchaseLine(models.Model):
    purchase = models.ForeignKey(Purchase,on_delete=models.PROTECT,related_name='lines')
    variant = models.ForeignKey(Variant,on_delete=models.PROTECT)
    inventory = models.ForeignKey(Inventory,on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=12,decimal_places=2)
    released = models.BooleanField(default=False)
    consumed = models.BooleanField(default=False)

class PreorderAllocation(models.Model):
    release = models.ForeignKey('preorders.Release',on_delete=models.PROTECT,related_name='variant_allocations')
    variant = models.ForeignKey(Variant,on_delete=models.PROTECT)
    capacity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['release','variant'],name='vc_unique_release_variant'),models.CheckConstraint(condition=Q(reserved__lte=F('capacity')),name='vc_preorder_reserved_capacity')]

class VariantPreorder(models.Model):
    class State(models.TextChoices):
        RESERVED='reserved','Reserved, unpaid'
        CANCELLED='cancelled','Cancelled'
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    allocation = models.ForeignKey(PreorderAllocation,on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=12,choices=State.choices,default=State.RESERVED)
    idempotency_key = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','idempotency_key'],name='vc_unique_preorder_key')]
