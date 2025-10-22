"""
Django settings for django_images project.
"""
import os
from dotenv import load_dotenv
from pathlib import Path
# Додатковий імпорт для перевірки налаштувань
from django.utils.functional import LazyObject
from django.conf import settings  # Потрібен для перевірки, чи налаштування вже існує
# Імпорт для створення користувацького сховища
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


# --- КЛАС СХОВИЩА ДЛЯ ВИПРАВЛЕННЯ ПОМИЛКИ ADMIN / WHITENOISE ---
# ManifestStaticFilesStorage викликає ValueError, коли не може знайти файл,
# на який посилається CSS (як-от admin/img/sorting-icons.svg).
# Цей клас-нащадок виключає всі файли, що належать додатку 'admin',
# з процесу пост-обробки, запобігаючи помилці.
class CustomManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Вимикає пост-обробку для статичних файлів адміністратора, щоб уникнути
    ValueError: The file 'admin/img/sorting-icons.svg' could not be found...
    """

    def post_process(self, *args, **kwargs):
        # Отримуємо ітератор для пост-обробки
        processed_files = super().post_process(*args, **kwargs)

        # Перевіряємо та ігноруємо файли, що належать додатку 'admin'
        for original_name, processed_name, processed in processed_files:
            if original_name.startswith('admin/'):
                # Пропускаємо файли admin, повертаючи успіх
                yield original_name, processed_name, True
            else:
                yield original_name, processed_name, processed


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 1. ЗАВАНТАЖЕННЯ ЗМІННИХ ОТОЧЕННЯ (.env) ---
# Переконайтеся, що файл .env існує і містить CLOUDINARY_URL
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# !!! УВАГА: При запуску Gunicorn (режим продакшену) DEBUG має бути False.
DEBUG = True

# !!! ВИПРАВЛЕННЯ 400 Bad Request: Необхідно вказати дозволені хости !!!
# Додайте домени або IP-адреси, з яких ви отримуєте доступ до сервера.
# У продакшені замініть '*' на конкретні домени (наприклад, ['mydomain.com', '10.0.0.1'])
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Application definition

INSTALLED_APPS = [
    # Власні налаштування
    "tailwind",
    "theme",
    "home",

    # Cloudinary
    "cloudinary_storage",
    "cloudinary",

    # Django Base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Django Browser Reload (для розробки)
# !!! УМОВНО ДОДАЄМО django_browser_reload ТІЛЬКИ, ЯКЩО DEBUG = True !!!
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

# --- TAILWIND CONFIG ---
TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = [
    "127.0.0.1",  # Localhost для django_browser_reload
]

NPM_BIN_PATH = "npm.cmd"

# --- MIDDLEWARE ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # !!! ДОДАНО WHITENOISE ДЛЯ ОБСЛУГОВУВАННЯ СТАТИЧНИХ ФАЙЛІВ В ПРОДАКШЕНІ !!!
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# !!! УМОВНО ДОДАЄМО BrowserReloadMiddleware ТІЛЬКИ, ЯКЩО DEBUG = True !!!
if DEBUG:
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

ROOT_URLCONF = "django_images.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Використовуйте Path для чистоти
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

WSGI_APPLICATION = "django_images.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# --- STATIC FILES (CSS, JS) ---
STATIC_URL = "static/"
# !!! ВИПРАВЛЕННЯ: Це обов'язково для 'staticfiles' та 'whitenoise' !!!
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- MEDIA FILES (Зображення, завантажені користувачами) ---

# 1. Cloudinary URL
# Змінна CLOUDINARY_URL повинна бути доступна в середовищі (з .env)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

# 2. Налаштування MEDIA URL
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"  # Цей каталог використовується тільки в розробці, коли Cloudinary вимкнено

# 3. Додаткова конфігурація Cloudinary (не обов'язкова, але корисна для деяких функцій)
if CLOUDINARY_URL:
    CLOUDINARY_STORAGE = {
        'CLOUDINARY_URL': CLOUDINARY_URL
    }
else:
    # Запобігання помилкам, якщо Cloudinary URL не встановлено
    print("WARNING: CLOUDINARY_URL environment variable is not set. Media files will fail to upload/serve.")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# !!! ОНОВЛЕНА КОНФІГУРАЦІЯ STORAGES (Django 4.2+) !!!
STORAGES = {
    # Сховище для медіа-файлів (за замовчуванням)
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    # Сховище для статичних файлів: використовуємо наш користувацький клас
    "staticfiles": {
        "BACKEND": "django_images.settings.CustomManifestStaticFilesStorage",
    },
}

# --- ВИПРАВЛЕННЯ СУМІСНОСТІ (CLOUDIDNARY / СТОРІННІ ПАКЕТИ) ---
if not hasattr(settings, 'STATICFILES_STORAGE'):
    try:
        STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]
    except KeyError:
        STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
