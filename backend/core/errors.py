"""统一错误结构与 DRF 异常处理。

所有 API 失败响应都遵循：
{ok: false, request_id, error: {code, message, retry_after?}}
"""
import logging
import uuid

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

log = logging.getLogger(__name__)


class ApiError(Exception):
    """业务错误：由视图或服务层主动抛出，携带对外可见的错误码。"""

    status_code = 400
    code = "INTERNAL_ERROR"
    default_message = "服务开小差了，请稍后再试"

    def __init__(self, message=None, *, code=None, status_code=None,
                 retry_after=None, field=None):
        self.message = message or self.default_message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.retry_after = retry_after
        self.field = field
        super().__init__(self.message)

    def payload(self, request_id):
        error = {"code": self.code, "message": self.message}
        if self.retry_after:
            error["retry_after"] = int(self.retry_after)
        if self.field:
            error["field"] = self.field
        return {"ok": False, "request_id": request_id, "error": error}


class InvalidInput(ApiError):
    status_code = 400
    code = "INVALID_INPUT"
    default_message = "请求参数不合法"


class RateLimited(ApiError):
    status_code = 429
    code = "RATE_LIMITED"
    default_message = "请求过于频繁，请稍后再试"


class ModelNotAllowed(ApiError):
    status_code = 400
    code = "MODEL_NOT_ALLOWED"
    default_message = "该模型不在可用白名单中"


class UpstreamTimeout(ApiError):
    status_code = 504
    code = "UPSTREAM_TIMEOUT"
    default_message = "上游模型响应超时，请重试"


class UpstreamQuota(ApiError):
    status_code = 502
    code = "UPSTREAM_QUOTA"
    default_message = "第三方模型额度或频率受限，请稍后再试"


class UpstreamError(ApiError):
    status_code = 502
    code = "UPSTREAM_ERROR"
    default_message = "上游模型返回异常"


class ContentBlocked(ApiError):
    status_code = 400
    code = "CONTENT_BLOCKED"
    default_message = "内容未通过安全校验，请调整描述后重试"


class NotFound(ApiError):
    status_code = 404
    code = "NOT_FOUND"
    default_message = "接口不存在"


def _request_id(request):
    request_id = getattr(request, "request_id", "") if request else ""
    return request_id or uuid.uuid4().hex[:16]


def api_exception_handler(exc, context):
    """把一切异常收敛成统一 JSON，避免把上游细节泄露给前端。"""
    request = context.get("request")
    request_id = _request_id(request)

    if isinstance(exc, ApiError):
        response = Response(exc.payload(request_id), status=exc.status_code)
        response["X-Request-ID"] = request_id
        if exc.retry_after:
            response["Retry-After"] = str(int(exc.retry_after))
        return response

    response = drf_exception_handler(exc, context)
    if response is not None:
        detail = getattr(exc, "detail", None)
        message = _detail_to_text(detail) or "请求参数不合法"
        body = {
            "ok": False,
            "request_id": request_id,
            "error": {"code": "INVALID_INPUT", "message": message},
        }
        response.data = body
        response["X-Request-ID"] = request_id
        return response

    log.exception("unhandled api error request_id=%s", request_id)
    response = Response(
        {
            "ok": False,
            "request_id": request_id,
            "error": {"code": "INTERNAL_ERROR", "message": "服务暂时不可用，请稍后重试"},
        },
        status=500,
    )
    response["X-Request-ID"] = request_id
    return response


def _detail_to_text(detail):
    if isinstance(detail, str):
        return detail
    if isinstance(detail, (list, tuple)):
        return "；".join(_detail_to_text(item) for item in detail)
    if isinstance(detail, dict):
        parts = []
        for key, value in detail.items():
            parts.append(f"{key}: {_detail_to_text(value)}")
        return "；".join(parts)
    return str(detail)
