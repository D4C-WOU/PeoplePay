"""
Django settings for the PeoplePay360 backend.

This file contains the application's development configuration:
- Django apps
- PostgreSQL database
- Django REST Framework
- JWT authentication
- CORS for the Next.js frontend
- Static files
"""

from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

# Load values from backend/.env when it exists.
load_dotenv()


# Build paths inside the project.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Basic development settings
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-peoplepay360-development-key",
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Allow Django to receive requests from the local development servers.
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django built-in applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party applications
    "rest_framework",
    "corsheaders",
    # PeoplePay360 applications
    "users",
    "employees",
    "contracts",
    "attendance",
    "time_off",
    "payroll",
    "seed",
    "api",
]


# PeoplePay360 uses its own User model.
AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Must be before CommonMiddleware so CORS headers are added
    # to responses sent to the Next.js frontend.
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
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


# ---------------------------------------------------------------------------
# PostgreSQL database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "peoplepay360"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    # PeoplePay360 authenticates API requests using JWT access tokens.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # API endpoints require authentication unless an endpoint explicitly
    # overrides this permission.
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Convert permission errors into the application's standard response.
    "EXCEPTION_HANDLER": "api.exceptions.custom_exception_handler",
}


# ---------------------------------------------------------------------------
# JWT authentication
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    # Access tokens are short-lived for normal API requests.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    # Refresh tokens allow the frontend to obtain a new access token
    # without forcing the user to log in again.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
#
# The Next.js development server normally runs on port 3000.
#
# Without this configuration the browser blocks:
#
#   http://localhost:3000
#          ↓
#   http://localhost:8000
#
# even though Django itself is running correctly.
#

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Also allow common alternate Next.js development ports.
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:30\d\d$",
    r"^http://127\.0\.0\.1:30\d\d$",
]


# ---------------------------------------------------------------------------
# CSRF trusted origins
# ---------------------------------------------------------------------------
#
# JWT authentication does not use Django's session CSRF mechanism for
# normal API requests, but keeping the local frontend trusted here avoids
# confusing CSRF failures if Django's browser-based features are used.
#

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
