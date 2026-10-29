"""限流：每 IP 每分钟 + 每匿名 ID 每日。

计数放在 Django cache（默认本地内存）。多 worker 场景请替换为 Redis，
否则实际额度约为「配置值 × worker 数」，README 中有说明。
"""
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .errors import RateLimited


def _incr(key: str, timeout: int) -> int:
    try:
        return cache.incr(key)
    except ValueError:
        cache.add(key, 1, timeout)
        return cache.get(key, 1) or 1


def _minute_key(ip_hash: str) -> str:
    now = timezone.localtime()
    return f"rl:m:{ip_hash}:{now.strftime('%Y%m%d%H%M')}"


def _day_key(anonymous_id: str) -> str:
    today = timezone.localdate().isoformat()
    return f"rl:d:{anonymous_id}:{today}"


def _seconds_to_next_minute() -> int:
    now = timezone.localtime()
    return max(1, 60 - now.second)


def _seconds_to_midnight() -> int:
    now = timezone.localtime()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((tomorrow - now).total_seconds()))


def consume(ip_hash: str, anonymous_id: str) -> dict:
    """先消费额度，超限抛 RateLimited。返回剩余次数。"""
    per_minute = settings.RATE_LIMIT_PER_MINUTE
    per_day = settings.RATE_LIMIT_PER_DAY

    minute_count = _incr(_minute_key(ip_hash), 70)
    if minute_count > per_minute:
        retry_after = _seconds_to_next_minute()
        raise RateLimited(
            f"请求过于频繁，每个网络每分钟最多 {per_minute} 次，请 {retry_after} 秒后再试",
            retry_after=retry_after,
        )

    day_count = _incr(_day_key(anonymous_id), _seconds_to_midnight() + 120)
    if day_count > per_day:
        retry_after = _seconds_to_midnight()
        raise RateLimited(
            f"今日额度已用完，每个匿名访客每天最多 {per_day} 次，请明天再来",
            retry_after=retry_after,
        )

    return {
        "perMinute": per_minute,
        "perDay": per_day,
        "minuteRemaining": max(0, per_minute - minute_count),
        "dayRemaining": max(0, per_day - day_count),
    }


def peek(ip_hash: str, anonymous_id: str) -> dict:
    """只读取剩余额度，不消费。"""
    per_minute = settings.RATE_LIMIT_PER_MINUTE
    per_day = settings.RATE_LIMIT_PER_DAY
    minute_count = cache.get(_minute_key(ip_hash), 0) or 0
    day_count = cache.get(_day_key(anonymous_id), 0) or 0
    return {
        "perMinute": per_minute,
        "perDay": per_day,
        "minuteRemaining": max(0, per_minute - minute_count),
        "dayRemaining": max(0, per_day - day_count),
        "resetsIn": _seconds_to_next_minute(),
        "dayResetsIn": _seconds_to_midnight(),
    }


def reset_all() -> None:
    """仅用于测试/运维排查。"""
    cache.clear()
