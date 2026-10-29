"""为每个请求生成可追踪的 request_id，并回写到响应头。"""
import re
import uuid

HEADER = "HTTP_X_REQUEST_ID"
SAFE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.META.get(HEADER, "")
        request.request_id = (
            incoming if SAFE_PATTERN.match(incoming or "") else uuid.uuid4().hex[:16]
        )
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response
