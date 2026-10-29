"""生成服务：串联模板、校验、演示模式与真实转发。"""
import json
from pathlib import Path

from django.conf import settings

from . import mock_engine, providers
from .errors import InvalidInput, UpstreamError
from .tooling import (
    MAX_TOKENS,
    TOOL_LABELS,
    build_image_prompt,
    build_messages,
)

TEMPLATES_PATH = Path(__file__).resolve().parent / "templates.json"
_templates_cache = {"mtime": None, "data": None}


def load_templates() -> dict:
    try:
        mtime = TEMPLATES_PATH.stat().st_mtime
    except OSError:
        return {"version": 1, "templates": []}
    if _templates_cache["mtime"] == mtime and _templates_cache["data"]:
        return _templates_cache["data"]
    try:
        data = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": 1, "templates": []}
    _templates_cache.update(mtime=mtime, data=data)
    return data


def resolve_template(template_id, tool: str) -> dict | None:
    if not template_id:
        return None
    template_id = str(template_id).strip()
    for template in load_templates().get("templates", []):
        if template.get("id") == template_id:
            if template.get("tool") != tool:
                raise InvalidInput("模板与当前工具不匹配", field="template_id")
            return template
    raise InvalidInput("模板不存在或已下线", field="template_id")


def generate(tool: str, model: dict, cleaned: dict, template: dict | None) -> dict:
    if tool not in TOOL_LABELS:
        raise InvalidInput("未知工具类型")

    if tool == "image":
        prompt = build_image_prompt(cleaned)
        if template:
            prompt = f"{template['content'][:400]}；{prompt}"
        if model["mock"]:
            images = mock_engine.mock_images(
                cleaned["prompt"], cleaned["style"], cleaned["size"], cleaned["count"]
            )
            return {"type": "image", "images": images, "text": "",
                    "usage": {}, "mock": True}
        images, usage = providers.image_generation(
            model, prompt, cleaned["size"], cleaned["count"],
            settings.UPSTREAM_IMAGE_TIMEOUT_SECONDS,
        )
        return {"type": "image", "images": images, "text": "",
                "usage": usage, "mock": False}

    if model["mock"]:
        text = mock_engine.mock_text(tool, cleaned)
        return {"type": "text", "text": text, "images": [], "usage": {}, "mock": True}

    messages = build_messages(tool, cleaned, template)
    if not model.get("base_url"):
        raise UpstreamError("模型配置不完整，请联系站点管理员")
    text, usage = providers.text_completion(
        model, messages, MAX_TOKENS.get(tool, 900), settings.UPSTREAM_TIMEOUT_SECONDS
    )
    return {"type": "text", "text": text, "images": [], "usage": usage, "mock": False}
