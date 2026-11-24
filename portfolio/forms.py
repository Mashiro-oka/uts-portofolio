from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import format_html
from PIL import Image

from .models import ContactMessage, Project


class AdminAuthenticationForm(AuthenticationForm):
    invalid_login_message = format_html(
        "Masukkan username dan kata sandi yang benar kalau kamu <strong>{}</strong>! 🍙",
        "Onigiryaa",
    )
    error_messages = {
        "invalid_login": invalid_login_message,
        "inactive": invalid_login_message,
    }

    def get_invalid_login_error(self):
        return forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise self.get_invalid_login_error()


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "body")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "body": forms.Textarea(attrs={"rows": 4}),
        }


class ProjectForm(forms.ModelForm):
    image_upload = forms.FileField(
        label="Gambar proyek", required=False,
        widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-image-upload": ""}),
        help_text="Pilih JPG, PNG, atau WebP dari perangkat. Maksimum 2 MB.",
    )
    remove_image = forms.BooleanField(label="Hapus gambar yang ada", required=False)
    image_types = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}

    class Meta:
        model = Project
        fields = (
            "title", "category", "summary", "description", "repository_url", "published",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 7})}

    def clean_image_upload(self):
        upload = self.cleaned_data["image_upload"]
        if upload is None:
            return None
        if upload.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Ukuran gambar maksimum 2 MB.")
        try:
            with Image.open(upload.file, formats=list(self.image_types)) as image:
                if image.width * image.height > 16_000_000:
                    raise forms.ValidationError("Resolusi gambar maksimum 16 megapiksel.")
                content_type = self.image_types[image.format]
                image.load()
        except (OSError, SyntaxError, ValueError, Image.DecompressionBombError) as error:
            raise forms.ValidationError("Pilih gambar JPG, PNG, atau WebP yang valid.") from error
        upload.seek(0)
        return upload.read(), content_type

    def clean(self):
        data = super().clean()
        if data.get("image_upload") and data.get("remove_image"):
            self.add_error(
                "remove_image",
                "Kosongkan pilihan ini jika Anda mengunggah gambar pengganti.",
            )
        return data
