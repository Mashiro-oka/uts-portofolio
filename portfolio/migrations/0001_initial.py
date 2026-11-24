import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nama')),
                ('email', models.EmailField(max_length=254, verbose_name='Alamat email')),
                ('body', models.TextField(max_length=2500, verbose_name='Pesan')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Judul proyek')),
                ('category', models.CharField(max_length=60, verbose_name='Kategori')),
                ('summary', models.CharField(max_length=240, verbose_name='Ringkasan')),
                ('description', models.TextField(max_length=5000, verbose_name='Deskripsi proyek')),
                ('link', models.URLField(blank=True, verbose_name='Tautan proyek')),
                ('published', models.BooleanField(default=False, verbose_name='Tampilkan di portofolio')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.BinaryField()),
                ('content_type', models.CharField(max_length=32)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='portfolio.project')),
            ],
        ),
    ]
