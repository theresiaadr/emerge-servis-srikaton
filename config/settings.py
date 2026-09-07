"""
Settings Web Report Sales Srikaton.
Keamanan diterapkan sejak awal (PRD section 12) — belajar dari insiden
DEBUG=1 di servis-srikaton.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Kredensial dari environment (.env), TIDAK di-hardcode -------------------
def env(key, default=""):
    return os.environ.get(key, default)

SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-ganti-di-produksi-xxxxxxxxxxxx")

# DEBUG default 0 (aman). Di dev, set DJANGO_DEBUG=1 di .env
DEBUG = env("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [h.strip() for h in env(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
).split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in env(
    "DJANGO_CSRF_TRUSTED_ORIGINS", ""
).split(",") if o.strip()]

# --- Aplikasi ----------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "captcha",
    "report",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "report.context_processors.reminder_badge",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ----------------------------------------------------------------
# Default SQLite (dev). Di produksi pakai PostgreSQL via env.
if env("DB_ENGINE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", "report_srikaton"),
            "USER": env("DB_USER", ""),
            "PASSWORD": env("DB_PASSWORD", ""),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Auth --------------------------------------------------------------------
AUTH_USER_MODEL = "report.User"

# AI-1: Proteksi brute-force login (django-axes)
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # jam
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# N-1: axes.W006 muncul krn AXES_LOCKOUT_PARAMETERS cuma "username"
# (bukan ip_address) — sengaja, biar lockout ngikutin akun bukan IP kantor
# yang dipakai bareng-bareng (banyak sales satu WiFi/NAT sama).
SILENCED_SYSTEM_CHECKS = ["axes.W006"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n / timezone ---------------------------------------------------------
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

# --- Static ------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Keamanan (aktif hanya saat produksi / DEBUG=0) --------------------------
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# Session timeout 2 jam idle (konsisten dgn servis-srikaton)
SESSION_COOKIE_AGE = 2 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True

if not DEBUG:
    SECURE_SSL_REDIRECT = env("DJANGO_SSL_REDIRECT", "0") == "1"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"

# --- Enkripsi field (AI-2) ---------------------------------------------------
# Kunci Fernet untuk EncryptedTextField (catatan & no_wa).
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DJANGO_FIELD_ENCRYPTION_KEY = env("DJANGO_FIELD_ENCRYPTION_KEY", "")

# --- Sentry (opsional, aktif kalau SENTRY_DSN diisi) — PRD section 12 --------
SENTRY_DSN = env("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=False,
        traces_sample_rate=1.0,
    )
