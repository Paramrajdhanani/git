import os
from pathlib import Path
from dotenv import load_dotenv


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# LOAD .ENV
# ==========================================================

load_dotenv(BASE_DIR / ".env", override=True)


# ==========================================================
# SECURITY
# ==========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-github-finder-ultra-secret-key-change-in-production-2026"
)

DEBUG = os.getenv("DEBUG", "True").lower() in (
    "true",
    "1",
    "yes",
    "on",
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]


# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "finder.apps.FinderConfig",
    "accounts.apps.AccountsConfig",
    "dashboard.apps.DashboardConfig",
    "history.apps.HistoryConfig",
    "favorites.apps.FavoritesConfig",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================================
# URL / WSGI
# ==========================================================

ROOT_URLCONF = "github_finder.urls"

WSGI_APPLICATION = "github_finder.wsgi.application"


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "finder.context_processors.global_context",
            ],
        },
    },
]


# ==========================================================
# DATABASE
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ==========================================================
# INTERNATIONALIZATION
# ==========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================================================
# CACHE
# ==========================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "github-finder-cache",
    }
}


# ==========================================================
# LOGIN / LOGOUT
# ==========================================================

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "dashboard:index"

LOGOUT_REDIRECT_URL = "finder:home"


# ==========================================================
# GITHUB API
# ==========================================================

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
).strip()


# ==========================================================
# GMAIL EMAIL OTP
# ==========================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

# IMPORTANT:
# Use the ENVIRONMENT VARIABLE NAME here,
# NOT your actual email address.

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    ""
).strip()

# IMPORTANT:
# Use the ENVIRONMENT VARIABLE NAME here,
# NOT the actual App Password.

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    ""
).strip()

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
).strip()

EMAIL_TIMEOUT = 30


# ==========================================================
# EMAIL DEBUG INFORMATION
# ==========================================================

print("========================================")
print("GMAIL CONFIGURATION")
print("========================================")
print(
    "EMAIL_HOST_USER:",
    repr(EMAIL_HOST_USER)
)
print(
    "PASSWORD EXISTS:",
    bool(EMAIL_HOST_PASSWORD)
)
print(
    "PASSWORD LENGTH:",
    len(EMAIL_HOST_PASSWORD)
)
print(
    "DEFAULT_FROM_EMAIL:",
    repr(DEFAULT_FROM_EMAIL)
)
print("========================================")


# ==========================================================
# SECURITY SETTINGS FOR PRODUCTION
# ==========================================================

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# ==========================================================
# WHITENOISE
# ==========================================================

WHITENOISE_USE_FINDERS = True

WHITENOISE_AUTOREFRESH = DEBUG
