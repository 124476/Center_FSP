import os
from pathlib import Path

from dotenv import load_dotenv

from django.utils.translation import gettext_lazy as _

load_dotenv()


def load_bool(name, default):
    env_value = os.getenv(name, default=str(default)).lower()
    return env_value in ("true", "yes", "1", "y", "t", "on")


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", default="no_key")

DEBUG = load_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="*").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "feedback.apps.FeedbackConfig",
    "users.apps.UsersConfig",
    "homepage.apps.HomepageConfig",
    "meropriations.apps.MeropriationsConfig",
    "meropriations_calendar.apps.MeropriationsCalendarConfig",
    "active_link",
    "sorl.thumbnail",
    "allauth",
    "allauth.account",
    'django.contrib.postgres',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "center_fsp.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "center_fsp.wsgi.application"


if os.getenv("USE_DOCKER") == "True":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
            'PORT': os.getenv('POSTGRES_PORT', 5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" 
        ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" 
        ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" 
        ".NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static_dev"]
STATIC_ROOT = "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

LOCALE_PATHS = (BASE_DIR / "locale/",)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "<[Center FSP]> "
SITE_ID = 1

EMAIL_HOST = os.getenv("MAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = os.getenv("MAIL_PORT", default=2525)
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = os.getenv("MAIL_USER", default="webmaster@localhost")
EMAIL_HOST_USER = os.getenv("MAIL_USER", default="webmaster@localhost")
EMAIL_HOST_PASSWORD = os.getenv(
    "MAIL_PASSWORD",
    default="this_very_secret_password_for_smtp_mail",
)
MAIL_PASSWORD = os.getenv(
    "MAIL_PASSWORD",
    default="this_very_secret_password_for_smtp_mail",
)