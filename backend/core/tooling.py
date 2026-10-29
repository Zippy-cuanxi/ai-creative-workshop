"""工具字段校验与 Prompt 组装。

字段规则与前端 src/data/tools.js 保持一致；后端以这里为准做二次校验。
"""
import re

from django.conf import settings

from .errors import ContentBlocked, InvalidInput

STYLES_NAME = {"创意", "稳重", "国潮", "科技", "可爱"}
PLATFORMS = {"公众号", "小红书", "短视频", "海报", "通用"}
REWRITE_STYLES = {"更口语", "更正式", "更简洁", "更有感染力"}
STRENGTHS = {"轻度", "中度", "深度"}
IMAGE_STYLES = {"写实摄影", "电影感", "扁平插画", "3D 渲染", "水彩", "国潮插画", "像素风"}
IMAGE_SIZES = {"1024x1024", "1536x1024", "1024x1536"}
COPY_LENGTHS = {"短", "中", "长"}

TOOL_LABELS = {"name": "起名", "copy": "文案", "rewrite": "改写", "image": "图片"}
TOOL_TYPES = {"name": "text", "copy": "text", "rewrite": "text", "image": "image"}

MAX_TOKENS = {"name": 900, "copy": 1200, "rewrite": 1200, "image": 0}

SYSTEM_PROMPT = (
    "你是「AI 创意工坊」的创意助手，服务对象是高校社团成员、协会成员与普通访客。\n"
    "硬性要求：\n"
    "1. 全程使用简体中文，语气专业、友好、可直接使用。\n"
    "2. 不要使用 emoji、颜文字或花哨符号，不使用 Markdown 表格。\n"
    "3. 直接给出成品与必要的说明，不要复述你的思考过程，不要提及本提示词。\n"
    "4. 拒绝暴力、违法、色情、歧视、危险行为等内容；遇到此类请求时只做简短拒绝。\n"
    "5. 结构清晰：使用简短小标题或编号列表，避免冗长套话。"
)


def _text(data, key: str, label: str, *, max_len: int, required: bool = True,
          min_len: int = 1) -> str:
    raw = data.get(key, "")
    if raw is None:
        raw = ""
    if not isinstance(raw, (str, int, float)):
        raise InvalidInput(f"「{label}」格式不正确", field=key)
    value = str(raw).strip()
    if required and len(value) < min_len:
        raise InvalidInput(f"请填写「{label}」", field=key)
    if len(value) > max_len:
        raise InvalidInput(f"「{label}」最多 {max_len} 个字符", field=key)
    return value


def _choice(data, key: str, label: str, options: set, default: str) -> str:
    value = str(data.get(key, default) or default).strip()
    if value not in options:
        raise InvalidInput(f"「{label}」只能是：{'、'.join(sorted(options))}", field=key)
    return value


def _number(data, key: str, label: str, *, minimum: int, maximum: int,
            default: int) -> int:
    raw = data.get(key, default)
    if raw in (None, ""):
        raw = default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise InvalidInput(f"「{label}」必须是数字", field=key)
    if not minimum <= value <= maximum:
        raise InvalidInput(f"「{label}」需在 {minimum}-{maximum} 之间", field=key)
    return value


def _safety_check(text: str) -> None:
    lowered = text.lower()
    for word in settings.CONTENT_BLOCKLIST:
        if word and word.lower() in lowered:
            raise ContentBlocked("内容包含不适合生成的关键词，请调整描述后重试")


def validate_input(tool: str, data) -> dict:
    if not isinstance(data, dict):
        raise InvalidInput("input 必须是对象")
    if tool == "name":
        cleaned = {
            "industry": _text(data, "industry", "行业 / 领域", max_len=40),
            "keywords": _text(data, "keywords", "关键词", max_len=80, required=False),
            "style": _choice(data, "style", "风格", STYLES_NAME, "创意"),
            "count": _number(data, "count", "数量", minimum=1, maximum=12, default=6),
            "avoid": _text(data, "avoid", "避用词", max_len=60, required=False),
            "extra": _text(data, "extra", "补充说明", max_len=300, required=False),
        }
    elif tool == "copy":
        cleaned = {
            "platform": _choice(data, "platform", "使用平台", PLATFORMS, "通用"),
            "topic": _text(data, "topic", "产品 / 主题", max_len=120),
            "audience": _text(data, "audience", "目标受众", max_len=60, required=False),
            "tone": _text(data, "tone", "语气", max_len=30, required=False) or "亲切自然",
            "length": _choice(data, "length", "长度", COPY_LENGTHS, "中"),
            "selling_points": _text(data, "selling_points", "核心卖点", max_len=300,
                                    required=False),
            "extra": _text(data, "extra", "补充要求", max_len=300, required=False),
        }
    elif tool == "rewrite":
        cleaned = {
            "source": _text(data, "source", "原文", max_len=2000, min_len=10),
            "style": _choice(data, "style", "改写风格", REWRITE_STYLES, "更口语"),
            "strength": _choice(data, "strength", "改写强度", STRENGTHS, "中度"),
            "keep": _text(data, "keep", "必须保留要点", max_len=200, required=False),
            "length_limit": _text(data, "length_limit", "长度限制", max_len=12,
                                  required=False),
        }
        if cleaned["length_limit"]:
            digits = re.sub(r"[^0-9]", "", cleaned["length_limit"])
            if not digits:
                raise InvalidInput("「长度限制」请填写数字（字数上限）", field="length_limit")
            limit = int(digits)
            if not 50 <= limit <= 2000:
                raise InvalidInput("「长度限制」需在 50-2000 字之间", field="length_limit")
            cleaned["length_limit"] = limit
    elif tool == "image":
        cleaned = {
            "prompt": _text(data, "prompt", "画面描述", max_len=500, min_len=2),
            "style": _choice(data, "style", "风格", IMAGE_STYLES, "电影感"),
            "size": _choice(data, "size", "尺寸", IMAGE_SIZES, "1024x1024"),
            "count": _number(data, "count", "数量", minimum=1, maximum=4, default=1),
            "negative": _text(data, "negative", "负面提示词", max_len=200, required=False),
        }
    else:
        raise InvalidInput("未知工具类型")

    _safety_check(" ".join(str(v) for v in cleaned.values()))
    return cleaned


def _points(value: str) -> list:
    if not value:
        return []
    parts = re.split(r"[、,，;；\n]+", value)
    return [p.strip() for p in parts if p.strip()]


def build_user_prompt(tool: str, cleaned: dict, template: dict | None) -> str:
    lines = []
    if template and template.get("content"):
        lines.append("【模板指令】")
        lines.append(str(template["content"])[:800])
        lines.append("")

    if tool == "name":
        lines += [
            "【任务】为下列对象起名，并给出寓意与使用建议。",
            f"行业 / 领域：{cleaned['industry']}",
            f"关键词：{cleaned['keywords'] or '无特别限定'}",
            f"风格：{cleaned['style']}",
            f"数量：{cleaned['count']} 个",
            f"避用词：{cleaned['avoid'] or '无'}",
            f"补充说明：{cleaned['extra'] or '无'}",
            "",
            "输出格式：命名思路（2 句）；备选名称（编号，每个名称后附 1 句寓意，"
            "可给英文写法）；使用建议（3 条，包含商标与口语测试提示）。",
        ]
    elif tool == "copy":
        lines += [
            "【任务】撰写可直接发布的文案。",
            f"平台：{cleaned['platform']}",
            f"主题 / 产品：{cleaned['topic']}",
            f"目标受众：{cleaned['audience'] or '普通读者'}",
            f"语气：{cleaned['tone']}",
            f"长度：{cleaned['length']}（短约 120 字，中约 300 字，长约 600 字）",
            f"核心卖点：{cleaned['selling_points'] or '请根据主题合理提炼'}",
            f"补充要求：{cleaned['extra'] or '无'}",
            "",
            "输出格式：给出 1 个标题（平台为小红书时给 2 个备选），正文按该平台的"
            "常见结构组织，最后给 3-5 个话题标签。",
        ]
    elif tool == "rewrite":
        limit = cleaned["length_limit"]
        lines += [
            "【任务】按要求改写原文，输出可直接替换使用的成品。",
            f"改写风格：{cleaned['style']}",
            f"改写强度：{cleaned['strength']}",
            f"必须保留要点：{cleaned['keep'] or '原文核心信息'}",
            f"长度限制：{'不超过 ' + str(limit) + ' 字' if limit else '与原文相近'}",
            "",
            "【原文】",
            cleaned["source"],
            "",
            "输出格式：先给「改写结果」，再给「改写说明」（3 条，说明做了哪些调整）。",
        ]
    elif tool == "image":
        lines += [
            "【任务】生成图片。",
            f"画面描述：{cleaned['prompt']}",
            f"风格：{cleaned['style']}",
            f"尺寸：{cleaned['size']}",
            f"数量：{cleaned['count']}",
            f"负面提示词：{cleaned['negative'] or '低质量、模糊、畸形、文字水印'}",
        ]
    return "\n".join(lines)


def build_messages(tool: str, cleaned: dict, template: dict | None) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(tool, cleaned, template)},
    ]


def build_image_prompt(cleaned: dict) -> str:
    parts = [cleaned["prompt"], f"风格：{cleaned['style']}"]
    if cleaned.get("negative"):
        parts.append(f"需要避免：{cleaned['negative']}")
    return "；".join(parts)
