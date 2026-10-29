"""调用记录模型：只存元数据，不存 prompt 与生成结果。"""
from django.db import models


class GenerationLog(models.Model):
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    STATUS_BLOCKED = "blocked"

    request_id = models.CharField(max_length=64, unique=True)
    anonymous_id = models.CharField(max_length=64, blank=True, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    tool = models.CharField(max_length=16)
    model = models.CharField(max_length=64)
    status = models.CharField(max_length=16)
    error_code = models.CharField(max_length=32, blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "调用记录"
        verbose_name_plural = "调用记录"
        indexes = [
            models.Index(fields=["ip_hash", "created_at"]),
            models.Index(fields=["anonymous_id", "created_at"]),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.tool} {self.status}"
