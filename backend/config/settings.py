"""AI 创意工坊 Django 配置。

后端职责刻意保持在“薄转发层”：密钥保护、转发、限流、调用元数据记录、统一错误码。
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _list(name: str, default: str = "") -> list:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key-please-change-in-production")
DEBUG = _bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = _list("DJANGO_ALLOWED_HOSTS", "*")

# 前端构建产物目录；配置后由 WhiteNoise + SPA 兜底视图直接托管（单容器部署）
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", str(BASE_DIR / "frontend_dist")))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestIdMiddleware",
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

DB_PATH = Path(os.getenv("DJANGO_SQLITE_PATH", str(BASE_DIR / "data" / "db.sqlite3")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DB_PATH),
        "OPTIONS": {"timeout": 20},
    }
}

# 限流计数默认放在本地内存缓存。多进程部署时建议替换为 Redis（见 README）。
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ai-creative-workshop",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# 单容器模式下，前端 dist 内的资源（/assets/xx.js）由 WhiteNoise 直接返回
WHITENOISE_ROOT = str(FRONTEND_DIST) if FRONTEND_DIST.exists() else None
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_MAX_AGE = 0 if DEBUG else 31536000

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "EXCEPTION_HANDLER": "core.errors.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

# CORS：默认只放行本地开发端口；生产用环境变量配置白名单
CORS_ALLOW_ALL_ORIGINS = _bool("CORS_ALLOW_ALL", DEBUG)
CORS_ALLOWED_ORIGINS = _list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-request-id",
]
CORS_EXPOSE_HEADERS = ["X-Request-ID"]

CSRF_TRUSTED_ORIGINS = _list("CSRF_TRUSTED_ORIGINS", "")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ---- 业务配置（全部可被环境变量覆盖）----
RATE_LIMIT_PER_MINUTE = _int("RATE_LIMIT_PER_MINUTE", 10)
RATE_LIMIT_PER_DAY = _int("RATE_LIMIT_PER_DAY", 100)
UPSTREAM_TIMEOUT_SECONDS = _int("UPSTREAM_TIMEOUT_SECONDS", 45)
UPSTREAM_IMAGE_TIMEOUT_SECONDS = _int("UPSTREAM_IMAGE_TIMEOUT_SECONDS", 90)
UPSTREAM_MAX_RETRIES = _int("UPSTREAM_MAX_RETRIES", 1)
LOG_GENERATION = _bool("LOG_GENERATION", True)
SHOW_UNAVAILABLE_MODELS = _bool("SHOW_UNAVAILABLE_MODELS", False)
MAX_INPUT_CHARS = _int("MAX_INPUT_CHARS", 8000)
CONTENT_BLOCKLIST = [w for w in _list(
    "CONTENT_BLOCKLIST",
    "制作炸弹,制毒,儿童色情,恐怖袭击,自制枪支",
) if w]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}
