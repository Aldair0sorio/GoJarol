from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('accounts', '0001_initial')]
    operations = [migrations.CreateModel(name='GoogleIdentity', fields=[
        ('subject', models.CharField(max_length=255, primary_key=True, serialize=False)),
        ('email', models.EmailField(max_length=254, unique=True)),
        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='google_identity', to=settings.AUTH_USER_MODEL)),
    ])]
