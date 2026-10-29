"""模型白名单与第三方 API 转发。

密钥只从环境变量读取，永不出现在响应里；模型列表通过 AI_MODELS_JSON 配置。
"""
import json
import logging
import os
import time

import requests
from django.conf import settings

from .errors import (
    ContentBlocked,
    ModelNotAllowed,
    UpstreamError,
    UpstreamQuota,
    UpstreamTimeout,
)

log = logging.getLogger(__name__)

MOCK_TEXT_MODEL = {
    "id": "mock-text",
    "name": "工坊示例模型（演示）",
    "provider": "mock",
    "type": "text",
    "upstream_model": "mock",
    "base_url": "",
    "api_key_env": "",
    "max_tokens": 1200,
    "mock": True,
}

MOCK_IMAGE_MODEL = {
    "id": "mock-image",
    "name": "工坊示例画师（演示）",
    "provider": "mock",
    "type": "image",
    "upstream_model": "mock",
    "base_url": "",
    "api_key_env": "",
    "max_tokens": 0,
    "mock": True,
}

PUBLIC_FIELDS = ("id", "name", "provider", "type", "mock")


def _normalize(raw: dict) -> dict | None:
    model_id = str(raw.get("id", "")).strip()
    if not model_id:
        return None
    provider = str(raw.get("provider", "openai")).strip() or "openai"
    model_type = "image" if str(raw.get("type", "text")).lower() == "image" else "text"
    return {
        "id": model_id,
        "name": str(raw.get("name") or model_id),
        "provider": provider,
        "type": model_type,
        "upstream_model": str(raw.get("upstream_model") or model_id),
        "base_url": str(raw.get("base_url") or "").rstrip("/"),
        "api_key_env": str(raw.get("api_key_env") or ""),
        "max_tokens": int(raw.get("max_tokens") or (900 if model_type == "text" else 0)),
        "mock": provider == "mock",
    }


def _configured_models() -> list:
    raw = os.getenv("AI_MODELS_JSON", "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except ValueError:
        log.warning("AI_MODELS_JSON 不是合法 JSON，已忽略并回落到演示模式")
        return []
    if isinstance(parsed, dict):
        parsed = parsed.get("models", [])
    if not isinstance(parsed, list):
        return []
    models = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        normalized = _normalize(item)
        if normalized:
            models.append(normalized)
    return models


def _has_credentials(model: dict) -> bool:
    if model["mock"]:
        return True
    if not model["base_url"]:
        return False
    return bool(os.getenv(model["api_key_env"], "").strip()) if model["api_key_env"] else False


def public_models() -> list:
    """对外暴露的模型白名单：只返回可用模型；某类型缺失时补上演示模型。"""
    available = [m for m in _configured_models() if _has_credentials(m)]
    if settings.SHOW_UNAVAILABLE_MODELS:
        available += [m for m in _configured_models() if not _has_credentials(m)]
    if not any(m["type"] == "text" for m in available):
        available.append(dict(MOCK_TEXT_MODEL))
    if not any(m["type"] == "image" for m in available):
        available.append(dict(MOCK_IMAGE_MODEL))
    return [{key: model[key] for key in PUBLIC_FIELDS} for model in available]


def get_model(model_id: str) -> dict:
    for model in public_models():
        if model["id"] == model_id:
            # 补齐内部字段（公开字段已过滤，这里重新取完整定义）
            for full in _configured_models() + [MOCK_TEXT_MODEL, MOCK_IMAGE_MODEL]:
                if full["id"] == model_id:
                    return full
    raise ModelNotAllowed("该模型不可用或不在白名单中，请刷新页面后重试")


def is_mock_only() -> bool:
    return all(model["provider"] == "mock" for model in public_models())


def _api_key(model: dict) -> str:
    key = os.getenv(model.get("api_key_env", ""), "").strip()
    if not key:
        raise UpstreamError("上游密钥未配置，请联系站点管理员")
    return key


def _post_json(url: str, payload: dict, api_key: str, timeout: int) -> dict:
    attempts = max(1, settings.UPSTREAM_MAX_RETRIES + 1)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    last_error = None
    for attempt in range(attempts):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.Timeout as exc:
            last_error = exc
            if attempt < attempts - 1:
                continue
            raise UpstreamTimeout("上游模型响应超时，请稍后重试或更换模型") from exc
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(0.6)
                continue
            raise UpstreamError("无法连接上游模型服务，请稍后重试") from exc

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "30")
            try:
                retry_after = int(retry_after)
            except ValueError:
                retry_after = 30
            raise UpstreamQuota(
                "第三方模型额度或频率受限，请稍后再试", retry_after=retry_after
            )
        if response.status_code >= 500:
            if attempt < attempts - 1:
                time.sleep(0.6)
                continue
            raise UpstreamError("上游模型服务暂时不可用，请稍后重试")
        if response.status_code >= 400:
            body = response.text[:500].lower()
            if any(word in body for word in ("moderation", "safety", "content_policy", "敏感")):
                raise ContentBlocked("内容未通过上游安全审核，请调整描述后重试")
            log.warning("upstream %s error: %s %s", url, response.status_code, response.text[:300])
            raise UpstreamError(f"上游服务拒绝了本次请求（HTTP {response.status_code}）")
        try:
            return response.json()
        except ValueError as exc:
            raise UpstreamError("上游返回内容格式异常") from exc
    raise UpstreamError("上游服务调用失败") from last_error


def text_completion(model: dict, messages: list, max_tokens: int, timeout: int) -> tuple:
    url = f"{model['base_url']}/chat/completions"
    payload = {
        "model": model["upstream_model"],
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": max_tokens or model["max_tokens"] or 900,
    }
    data = _post_json(url, payload, _api_key(model), timeout)
    choices = data.get("choices") or []
    if not choices:
        raise UpstreamError("上游没有返回可用结果，请重试")
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )
    text = str(content).strip()
    if not text:
        raise UpstreamError("上游返回了空结果，请重试")
    usage = data.get("usage") or {}
    return text, {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
    }


def image_generation(model: dict, prompt: str, size: str, count: int,
                     timeout: int) -> tuple:
    url = f"{model['base_url']}/images/generations"
    payload = {
        "model": model["upstream_model"],
        "prompt": prompt,
        "n": count,
        "size": size,
    }
    data = _post_json(url, payload, _api_key(model), timeout)
    items = data.get("data") or []
    images = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("url"):
            images.append(str(item["url"]))
        elif item.get("b64_json"):
            images.append(f"data:image/png;base64,{item['b64_json']}")
    if not images:
        raise UpstreamError("上游未返回图片，请调整描述后重试")
    return images, {}
