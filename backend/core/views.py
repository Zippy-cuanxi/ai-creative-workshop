"""API 视图：只做校验、限流、转发与记录。"""
import logging
import time

from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from . import providers, ratelimit, service
from .errors import ApiError, InvalidInput
from .models import GenerationLog
from .privacy import client_ip, hash_ip, is_valid_anonymous_id
from .tooling import TOOL_LABELS, TOOL_TYPES, validate_input

log = logging.getLogger(__name__)


def _limits() -> dict:
    return {
        "perMinute": settings.RATE_LIMIT_PER_MINUTE,
        "perDay": settings.RATE_LIMIT_PER_DAY,
    }


def _record(*, request_id: str, anonymous_id: str, ip_hash: str, tool: str,
            model: str, status: str, error_code: str = "", latency_ms: int = 0,
            usage: dict | None = None) -> None:
    """写库失败不影响主流程；也不记录 prompt / 正文。"""
    if not settings.LOG_GENERATION:
        return
    usage = usage or {}
    try:
        GenerationLog.objects.create(
            request_id=request_id,
            anonymous_id=anonymous_id[:64],
            ip_hash=ip_hash[:64],
            tool=tool[:16],
            model=model[:64],
            status=status,
            error_code=(error_code or "")[:32],
            latency_ms=max(0, int(latency_ms)),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
        )
    except Exception:  # pragma: no cover - 记录失败不阻断业务
        log.warning("调用记录写入失败 request_id=%s", request_id, exc_info=True)


class ModelsView(APIView):
    def get(self, request):
        models = providers.public_models()
        return Response({
            "ok": True,
            "models": models,
            "limits": _limits(),
            "demoMode": all(model["provider"] == "mock" for model in models),
        })


class TemplatesView(APIView):
    def get(self, request):
        data = service.load_templates()
        response = Response({
            "ok": True,
            "version": data.get("version", 1),
            "categories": data.get("categories", []),
            "templates": data.get("templates", []),
        })
        response["Cache-Control"] = "public, max-age=300"
        return response


class UsageView(APIView):
    def get(self, request):
        anonymous_id = str(request.query_params.get("anonymous_id", "")).strip()
        if not is_valid_anonymous_id(anonymous_id):
            raise InvalidInput("anonymous_id 不合法", field="anonymous_id")
        ip_hash = hash_ip(client_ip(request))
        usage = ratelimit.peek(ip_hash, anonymous_id)
        return Response({"ok": True, "limits": _limits(), "usage": usage})


class GenerateView(APIView):
    def post(self, request):
        payload = request.data
        if not isinstance(payload, dict):
            raise InvalidInput("请求体必须是 JSON 对象")

        tool = str(payload.get("tool", "")).strip()
        if tool not in TOOL_LABELS:
            raise InvalidInput("tool 必须是 name / copy / rewrite / image 之一", field="tool")

        anonymous_id = str(payload.get("anonymous_id", "")).strip()
        if not is_valid_anonymous_id(anonymous_id):
            raise InvalidInput("匿名标识不合法，请刷新页面后重试", field="anonymous_id")

        model = providers.get_model(str(payload.get("model", "")).strip())
        if model["type"] != TOOL_TYPES[tool]:
            raise InvalidInput("当前工具不支持该模型类型，请重新选择模型", field="model")

        cleaned = validate_input(tool, payload.get("input") or {})
        template = service.resolve_template(payload.get("template_id"), tool)

        ip_hash = hash_ip(client_ip(request))
        remaining = ratelimit.consume(ip_hash, anonymous_id)

        request_id = request.request_id
        started = time.monotonic()
        try:
            result = service.generate(tool, model, cleaned, template)
        except ApiError as exc:
            latency = int((time.monotonic() - started) * 1000)
            _record(
                request_id=request_id,
                anonymous_id=anonymous_id,
                ip_hash=ip_hash,
                tool=tool,
                model=model["id"],
                status="blocked" if exc.code == "CONTENT_BLOCKED" else "error",
                error_code=exc.code,
                latency_ms=latency,
            )
            raise
        except Exception:
            latency = int((time.monotonic() - started) * 1000)
            _record(
                request_id=request_id,
                anonymous_id=anonymous_id,
                ip_hash=ip_hash,
                tool=tool,
                model=model["id"],
                status="error",
                error_code="INTERNAL_ERROR",
                latency_ms=latency,
            )
            log.exception("generate failed request_id=%s", request_id)
            raise

        latency = int((time.monotonic() - started) * 1000)
        _record(
            request_id=request_id,
            anonymous_id=anonymous_id,
            ip_hash=ip_hash,
            tool=tool,
            model=model["id"],
            status="ok",
            latency_ms=latency,
            usage=result.get("usage"),
        )
        return Response({
            "ok": True,
            "request_id": request_id,
            "result": result,
            "usage": result.get("usage") or {},
            "remaining": remaining,
            "model": {
                "id": model["id"],
                "name": model["name"],
                "type": model["type"],
                "mock": model["mock"],
            },
            "latency_ms": latency,
        })


class HealthView(APIView):
    def get(self, request):
        models = providers.public_models()
        return Response({
            "ok": True,
            "status": "healthy",
            "service": "ai-creative-workshop",
            "version": "1.0.0",
            "time": timezone.now().isoformat(),
            "models": len(models),
            "demoMode": all(model["provider"] == "mock" for model in models),
            "logEnabled": settings.LOG_GENERATION,
        })
