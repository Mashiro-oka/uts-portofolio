from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import ContactMessage


@override_settings(ON_VERCEL=False, SECURE_SSL_REDIRECT=False)
class ContactRateLimitTests(TestCase):
    def test_limit_survives_clock_minute_change(self):
        start = datetime(2026, 1, 1, 12, 0, 59, tzinfo=timezone.utc)
        form = {"name": "Tamu", "email": "tamu@example.com", "body": "Pesan uji"}

        with patch("portfolio.rate_limits.timezone.now", return_value=start) as now:
            for _ in range(8):
                response = self.client.post("/", form, REMOTE_ADDR="192.0.2.10")
                self.assertRedirects(response, "/#contact", fetch_redirect_response=False)

            now.return_value = start + timedelta(seconds=1)
            response = self.client.post("/", form, REMOTE_ADDR="192.0.2.10")
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers["Retry-After"], "59")

            now.return_value = start + timedelta(seconds=2)
            response = self.client.post("/", form, REMOTE_ADDR="192.0.2.10")
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers["Retry-After"], "58")
            self.assertEqual(ContactMessage.objects.count(), 8)

            response = self.client.post("/", form, REMOTE_ADDR="192.0.2.11")
            self.assertRedirects(response, "/#contact", fetch_redirect_response=False)

            now.return_value = start + timedelta(seconds=60)
            response = self.client.post("/", form, REMOTE_ADDR="192.0.2.10")
            self.assertRedirects(response, "/#contact", fetch_redirect_response=False)

        self.assertEqual(ContactMessage.objects.count(), 10)


@override_settings(
    ON_VERCEL=False,
    SECURE_SSL_REDIRECT=False,
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class AdminLoginRateLimitTests(TestCase):
    def test_fifth_failure_blocks_next_login_until_slot_expires(self):
        start = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        get_user_model().objects.create_superuser(
            "tester", password="Test-only-password-2026"
        )
        url = "/admin/login/"
        correct = {"username": "tester", "password": "Test-only-password-2026"}
        wrong = {**correct, "password": "wrong-test-password"}
        address = {"REMOTE_ADDR": "192.0.2.10"}

        with patch("portfolio.rate_limits.timezone.now", return_value=start) as now:
            for _ in range(4):
                response = self.client.post(url, wrong, **address)
                self.assertEqual(response.status_code, 200)
                self.assertContains(
                    response,
                    "Masukkan username dan kata sandi yang benar kalau kamu "
                    "<strong>Onigiryaa</strong>! 🍙",
                    count=1,
                )
                self.assertContains(response, 'class="feedback login-warning"', count=1)

            response = self.client.post(url, correct, **address)
            self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
            self.client.post("/admin/logout/", **address)

            now.return_value = start + timedelta(seconds=5)
            self.assertEqual(self.client.post(url, wrong, **address).status_code, 200)

            response = self.client.post(url, correct, **address)
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers["Retry-After"], "595")
            self.assertContains(
                response,
                "Terdeteksi bukan <strong>Onigirya</strong>. Dilarang masuk! 🍙",
                count=1,
                status_code=429,
            )
            self.assertContains(response, 'class="feedback login-warning"', count=1, status_code=429)
            self.assertNotIn("_auth_user_id", self.client.session)

            now.return_value = start + timedelta(minutes=10)
            response = self.client.post(url, correct, **address)
            self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
