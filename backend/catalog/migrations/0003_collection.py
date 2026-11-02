from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_product_image")]
    operations = [
        migrations.CreateModel(
            name="Collection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("description", models.TextField(blank=True)),
                ("image", models.ImageField(upload_to="collections/%Y/%m/", blank=True, null=True)),
                ("active", models.BooleanField(default=False)),
                ("publish_from", models.DateTimeField(null=True, blank=True)),
                ("publish_until", models.DateTimeField(null=True, blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("products", models.ManyToManyField(blank=True, related_name="curated_collections", to="catalog.product")),
            ],
            options={"ordering": ["sort_order", "name", "id"]},
        ),
    ]