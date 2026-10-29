"""匿名化辅助：客户端 IP 提取与哈希、匿名 ID 校验。"""
import hashlib
import hmac
import re

from django.conf import settings

ANON_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "0.0.0.0"


def hash_ip(ip: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), ip.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:32]


def is_valid_anonymous_id(value: str) -> bool:
    return bool(value and ANON_PATTERN.match(value))


def mask_anonymous_id(value: str) -> str:
    if not value:
        return ""
    return value[:4] + "…" + value[-2:] if len(value) > 8 else value
