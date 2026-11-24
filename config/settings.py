import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured
from django.db.backends.signals import connection_created
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
ON_VERCEL = os.getenv("VERCEL") == "1"
DEBUG = not ON_VERCEL and os.getenv("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or ("athif-local-development" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY.")


def env_list(name):
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


vercel_hosts = [
    value
    for key in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL")
    if (value := os.getenv(key))
]
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"] + vercel_hosts + env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in vercel_hosts] + env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS"
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 300 if ON_VERCEL else 0
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portfolio",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"

database_url = os.getenv("DATABASE_URL")
if database_url:
    url = urlsplit(database_url)
    schema = os.getenv("DJANGO_DB_SCHEMA", "public")
    if (
        not re.fullmatch(r"[a-z_][a-z0-9_]*", schema)
        or url.scheme not in ("postgres", "postgresql")
        or not url.hostname
    ):
        raise ImproperlyConfigured("Use a PostgreSQL URL and a lowercase Django schema name.")
    database_options = {"sslmode": "require"}
    if root_certificate := os.getenv("DJANGO_DB_SSLROOTCERT"):
        database_options.update(sslmode="verify-full", sslrootcert=root_certificate)
    database = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(url.path.lstrip("/")),
        "USER": unquote(url.username or ""),
        "PASSWORD": unquote(url.password or ""),
        "HOST": url.hostname,
        "PORT": url.port or 5432,
        "OPTIONS": database_options,
    }

    def select_schema(sender, connection, **kwargs):
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO "{schema}"')

    connection_created.connect(select_schema, weak=False)
elif ON_VERCEL:
    raise ImproperlyConfigured("Set DATABASE_URL to the Supabase session pooler URL.")
else:
    database = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
DATABASES = {"default": database}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{validator}"}
    for validator in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "admin_login"
