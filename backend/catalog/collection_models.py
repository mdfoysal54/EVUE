from django.db import models
from django.utils import timezone
from .models import Product


class Collection(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="collections/%Y/%m/", blank=True, null=True)
    active = models.BooleanField(default=False)
    publish_from = models.DateTimeField(null=True, blank=True)
    publish_until = models.DateTimeField(null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    products = models.ManyToManyField(Product, related_name="curated_collections", blank=True)

    class Meta:
        ordering = ["sort_order", "name", "id"]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.publish_from and self.publish_until and self.publish_from >= self.publish_until:
            raise ValidationError({"publish_until": "End must follow start."})

    @classmethod
    def visible(cls):
        from django.db.models import Q
        now = timezone.now()
        return cls.objects.filter(active=True).filter(
            Q(publish_from__isnull=True) | Q(publish_from__lte=now),
            Q(publish_until__isnull=True) | Q(publish_until__gt=now),
        )

    def __str__(self):
        return self.name