from django.core.validators import URLValidator
from django.db import models


class Project(models.Model):
    title = models.CharField("Judul proyek", max_length=120)
    category = models.CharField("Kategori", max_length=60)
    summary = models.CharField("Ringkasan", max_length=240)
    description = models.TextField("Deskripsi proyek", max_length=5000)
    link = models.URLField("Tautan proyek", blank=True)
    repository_url = models.URLField(
        "URL repositori",
        max_length=500,
        blank=True,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    published = models.BooleanField("Tampilkan di portofolio", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.OneToOneField(Project, related_name="image", on_delete=models.CASCADE)
    content = models.BinaryField()
    content_type = models.CharField(max_length=32)
    updated_at = models.DateTimeField(auto_now=True)


class ContactMessage(models.Model):
    name = models.CharField("Nama", max_length=100)
    email = models.EmailField("Alamat email")
    body = models.TextField("Pesan", max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class SubmissionLimit(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)
