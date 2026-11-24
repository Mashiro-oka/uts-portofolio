import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='repository_url',
            field=models.URLField(blank=True, max_length=500, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])], verbose_name='URL repositori'),
        ),
    ]
