from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('operations', '0001_initial')]
    operations = [
        migrations.AddField('announcement', 'kind', models.CharField(max_length=20, default='general', choices=[('general','General'),('launch','Product launch'),('offer','Special offer'),('collection','Collection'),('service','Service update')])),
        migrations.AddField('announcement', 'placement', models.CharField(max_length=10, default='both', choices=[('bar','Announcement bar'),('home','Homepage'),('both','Both')])),
        migrations.AddField('announcement', 'slug', models.SlugField(max_length=180, unique=True, null=True, blank=True)),
        migrations.AddField('announcement', 'image', models.ImageField(upload_to='announcements/%Y/%m/', null=True, blank=True)),
        migrations.AddField('announcement', 'cta_label', models.CharField(max_length=70, blank=True)),
        migrations.AddField('announcement', 'cta_url', models.CharField(max_length=300, blank=True)),
        migrations.AddField('announcement', 'publish_from', models.DateTimeField(null=True, blank=True)),
        migrations.AddField('announcement', 'publish_until', models.DateTimeField(null=True, blank=True)),
        migrations.AddField('announcement', 'priority', models.PositiveSmallIntegerField(default=0)),
        migrations.CreateModel(name='NewsletterSubscription', fields=[('id', models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),('email',models.EmailField(unique=True,max_length=254)),('consented_at',models.DateTimeField(auto_now_add=True)),('active',models.BooleanField(default=True))]),
    ]