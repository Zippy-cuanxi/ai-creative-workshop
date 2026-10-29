"""演示模式（mock）：在没有配置第三方密钥时也能完整体验全部工具。

设计目标：
- 输出结构与真实模型接近，便于直接复制使用；
- 完全本地生成，不依赖网络，不产生第三方费用；
- 图片用自包含的 SVG data URI，不依赖外部图床。
"""
import base64
import html
import re
import textwrap

TOOL_SUFFIX = {
    "社团": ["社", "共创社", "青年社"],
    "协会": ["协会", "联盟", "工坊"],
    "咖啡": ["工坊", "小馆", "食集"],
    "茶": ["茶舍", "小馆", "工坊"],
    "烘焙": ["烘焙所", "食集", "工坊"],
    "品牌": ["品牌", "实验室", "计划"],
    "课程": ["课堂", "研习社", "计划"],
    "活动": ["计划", "企划", "现场"],
}

NAME_PREFIX = {
    "创意": [
        ("浮光", "取光线的流动感，轻盈、有想象空间"),
        ("奇点", "象征创意爆发的起点"),
        ("半野", "介于规整与自由之间，保留野生感"),
        ("未迟", "一切都还来得及，带有少年气"),
        ("回声", "强调被听见、被回应"),
        ("小满", "恰到好处，留有余地"),
        ("拾光", "把零散的好时光收起来"),
        ("无界", "不设边界，主打开放与跨界"),
    ],
    "稳重": [
        ("正和", "取正道与和气，稳妥可信"),
        ("恒远", "强调长期主义与持续经营"),
        ("厚德", "取自厚德载物，突出责任感"),
        ("中衡", "强调平衡与专业判断"),
        ("同源", "强调共同来源与协作"),
        ("久成", "长久积累，自然成事"),
        ("立言", "取立言立行，重承诺"),
        ("清和", "清爽平和，不张扬"),
    ],
    "国潮": [
        ("山河", "把地理与家国气韵写进名字"),
        ("青瓷", "取自宋代青瓷，温润克制"),
        ("见山", "取自见山是山，留白有意境"),
        ("归鹤", "仙鹤归巢，带东方浪漫"),
        ("云锦", "取织锦之意，华而不艳"),
        ("拾遗", "打捞被忽略的传统细节"),
        ("松间", "取自松间明月，清雅安静"),
        ("渡口", "有出发与相遇的画面感"),
    ],
    "科技": [
        ("矩阵", "强调结构与秩序感"),
        ("量子", "代表微小却关键的跃迁"),
        ("原点", "一切从这里开始"),
        ("星链", "连接成网，指向未来"),
        ("智核", "把智能放进内核"),
        ("极简", "少即是多，效率优先"),
        ("深蓝", "冷静、专业、可信"),
        ("脉冲", "短促有力，强调节奏"),
    ],
    "可爱": [
        ("团子", "软糯圆润，亲和力强"),
        ("软糖", "甜而不腻，记忆点强"),
        ("布丁", "Q 弹可爱，适合年轻客群"),
        ("喵吉", "带一点小动物式的俏皮"),
        ("小鹿", "清澈、灵动、不具攻击性"),
        ("圆圆", "形状感强，适合做视觉符号"),
        ("豆丁", "小巧亲切，口语传播成本低"),
        ("阿满", "像朋友的小名，容易亲近"),
    ],
}

COLLOQUIAL_MAP = [
    ("因此", "所以"), ("以及", "还有"), ("进行", "做"), ("是否", "是不是"),
    ("如需", "要是想"), ("此外", "另外"), ("目前", "现在"), ("较为", "挺"),
    ("显著", "很明显"), ("旨在", "主要是想"), ("通过", "用"), ("具有", "有"),
    ("从而", "这样"), ("基于", "根据"), ("倘若", "如果"), ("鉴于", "考虑到"),
    ("为此", "为了这件事"), ("陆续", "一个接一个"),
]

FORMAL_MAP = [
    ("挺", "较为"), ("特别", "尤为"), ("搞", "推进"), ("咱们", "我们"),
    ("啥", "什么"), ("很多", "大量"), ("差不多", "基本"), ("不行", "不可行"),
    ("说白了", "简而言之"), ("反正", "总之"), ("挺好", "较为理想"),
    ("超级", "非常"), ("老是", "频繁"), ("弄", "处理"),
]

FILLER = ["其实", "基本上", "真的", "非常", "十分", "的话", "就是说", "可以说", "说实话"]


# ---------------- 文本类 ----------------

def _points(value: str) -> list:
    if not value:
        return []
    return [p.strip() for p in re.split(r"[、,，;；\n]+", value) if p.strip()]


def _suffixes(industry: str, style: str) -> list:
    for key, items in TOOL_SUFFIX.items():
        if key in industry:
            return items
    if style == "国潮":
        return ["堂", "舍", "集"]
    if style == "可爱":
        return ["屋", "小铺", "乐园"]
    if style == "科技":
        return ["实验室", "引擎", "计划"]
    return ["工作室", "造物", "计划", "空间"]


def _mock_name(data: dict) -> str:
    industry = data["industry"]
    style = data["style"]
    count = data["count"]
    prefixes = NAME_PREFIX[style]
    suffixes = _suffixes(industry, style)
    names = []
    for index in range(count):
        prefix, meaning = prefixes[index % len(prefixes)]
        suffix = suffixes[index % len(suffixes)]
        names.append((f"{prefix}{suffix}", meaning))
    # 去重（数量大于组合数时允许重复前缀，此处仅做一次保护）
    seen, unique = set(), []
    for item in names:
        if item[0] in seen:
            continue
        seen.add(item[0])
        unique.append(item)

    lines = [
        "命名思路",
        f"面向「{industry}」，以「{style}」为基调：前缀取 2 字意象，后缀点明品类，"
        f"整体控制在 3-4 字，读音干净、便于口头传播"
        + (f"；同时避开「{data['avoid']}」。" if data["avoid"] else "。"),
        "",
        "备选名称",
    ]
    for index, (name, meaning) in enumerate(unique, start=1):
        lines.append(f"{index}. {name}")
        lines.append(f"   寓意：{meaning}；后缀明确指向「{industry}」的业务属性。")
    lines += [
        "",
        "使用建议",
        "1. 先在目标人群中做一次口头测试，确认没有负面谐音与理解偏差。",
        "2. 名称确定后尽快做商标近似查询，并检索域名、公众号与社交账号是否可用。",
        "3. 保留 1-2 个备选名，方便后续做系列产品或活动延展。",
    ]
    if data["extra"]:
        lines += ["", f"补充说明已考虑：{data['extra']}"]
    return "\n".join(lines)


def _copy_points(data: dict) -> list:
    points = _points(data["selling_points"])
    while len(points) < 3:
        defaults = [
            f"{data['topic']}的真实使用场景",
            "上手门槛低，第一次就能用",
            "有清楚的结果与反馈",
        ]
        points.append(defaults[len(points)])
    return points[:4]


def _mock_copy(data: dict) -> str:
    platform = data["platform"]
    topic = data["topic"]
    audience = data["audience"] or "目标读者"
    points = _copy_points(data)
    tone_line = f"整体语气：{data['tone']}。" if data["tone"] else ""

    if platform == "小红书":
        support_lines = [
            "真实体验是：不用准备太久，第一次就能上手，反馈也比较直接。",
            "身边同学的反馈是：门槛比想象中低，照着清单做就行。",
            "实际用下来：细节考虑得比较周到，遇到问题也有人答疑。",
        ]
        body = [
            f"标题备选",
            f"1. {topic}｜{audience}最关心的 3 个问题",
            f"2. 关于{topic}，我帮你先试了一遍",
            "",
            "正文",
            f"最近有{audience}反复问我：{topic}到底值不值得了解。我把它拆成 3 点，"
            f"看完大概就有答案了。",
            "",
        ]
        for index, point in enumerate(points, start=1):
            body.append(f"{index}. {point}")
            body.append(f"   {support_lines[(index - 1) % len(support_lines)]}")
        body += [
            "",
            f"如果你也在关注{topic}，建议先从最小的一步开始，不需要等到“准备好”。",
            "",
            "话题标签",
            f"#{topic.replace(' ', '')} #实用分享 #新手入门 #经验总结 #{audience.replace(' ', '')}",
        ]
        result = "\n".join(body)
    elif platform == "公众号":
        result = "\n".join([
            "标题",
            f"{topic}：给{audience}的一份实用说明",
            "",
            "导语",
            f"这段时间，{topic}被反复提起。这篇文章不堆概念，只讲清楚三件事："
            "它解决什么问题、为什么现在值得关注、以及怎么开始。",
            "",
            "一、它解决什么问题",
            f"对{audience}来说，最直接的收益是：{points[0]}。"
            "很多讨论停在名词层面，但真正的差别在于是否用起来。",
            "",
            "二、为什么现在值得关注",
            f"{points[1]}。当基础条件逐渐成熟，早一步尝试的成本会比想象中低。",
            "",
            "三、怎么开始",
            f"建议从最小的场景切入：{points[2]}。给自己设一个一周的小目标，"
            "比一次性做完整方案更容易坚持。",
            "",
            "写在最后",
            f"如果你身边也有{audience}在关注{topic}，欢迎把这篇内容转给 TA。",
        ])
    elif platform == "短视频":
        result = "\n".join([
            "封面文案",
            f"{topic}，3 个重点一次讲清",
            "",
            "分镜脚本",
            f"0-3 秒（钩子）：还在纠结{topic}？先别划走，这条讲人话。",
            f"3-12 秒（痛点）：{audience}最常见的卡点是——不知道怎么开始，"
            "也不知道做了有什么用。",
            f"12-25 秒（要点）：第一，{points[0]}；第二，{points[1]}；第三，{points[2]}。",
            f"25-35 秒（收尾）：想试试的话，先从最小的一步开始，"
            f"评论区告诉我你的场景，我帮你拆。",
            "",
            "拍摄提示",
            "竖屏构图，人物居中偏左，关键词用大字幕压在画面上三分之一；"
            "每 5 秒切一次景别，避免长时间固定镜头。",
        ])
    elif platform == "海报":
        result = "\n".join([
            "主标题",
            topic,
            "",
            "副标题",
            f"给{audience}的一个新选择",
            "",
            "利益点",
            f"- {points[0]}",
            f"- {points[1]}",
            f"- {points[2]}",
            "",
            "行动按钮",
            "立即了解",
            "",
            "视觉建议",
            "主标题用粗体大字占画面 40%，利益点用 3 行短句，留出足够白边；"
            "整体控制在 3 种颜色以内。",
        ])
    else:
        result = "\n".join([
            "标题",
            f"{topic}：{audience}需要知道的三件事",
            "",
            f"开头：如果你正在关注{topic}，这条内容可以帮你快速建立判断。{tone_line}",
            "",
            "三个重点",
            f"1. {points[0]}",
            f"2. {points[1]}",
            f"3. {points[2]}",
            "",
            "结尾",
            f"把{topic}放进你接下来一周的计划里，先做一个小实验，"
            "比停留在收藏夹更有效。",
        ])

    if data["extra"]:
        result += f"\n\n补充要求已处理：{data['extra']}"
    return result


def _split_sentences(text: str) -> list:
    return [s.strip() for s in re.findall(r"[^。！？!?；;\n]+[。！？!?；;]?", text) if s.strip()]


def _apply_map(text: str, mapping: list) -> str:
    for source, target in mapping:
        text = text.replace(source, target)
    return text


def _mock_rewrite(data: dict) -> str:
    source = data["source"]
    style = data["style"]
    strength = data["strength"]
    ratio = {"轻度": 0.35, "中度": 0.65, "深度": 1.0}[strength]
    sentences = _split_sentences(source)
    limit = min(len(sentences), max(1, round(ratio * len(sentences))))

    processed = []
    for index, sentence in enumerate(sentences):
        if index < limit:
            if style == "更口语":
                sentence = _apply_map(sentence, COLLOQUIAL_MAP)
                sentence = "说白了，" + sentence if index == 0 and "说白了" not in sentence else sentence
            elif style == "更正式":
                sentence = _apply_map(sentence, FORMAL_MAP)
                if index == 0:
                    sentence = "基于上述背景，" + sentence
            elif style == "更简洁":
                for filler in FILLER:
                    sentence = sentence.replace(filler, "")
            elif style == "更有感染力":
                if index == 0:
                    sentence = "如果把这件事讲得更直白一点：" + sentence
                elif index == 1:
                    sentence = "你可以想象一下：" + sentence
        processed.append(sentence)

    if style == "更简洁":
        processed = [s for s in processed if s]

    result_text = "".join(processed)
    limit_chars = data.get("length_limit") or 0
    truncated = False
    if limit_chars and len(result_text) > limit_chars:
        result_text = result_text[:limit_chars].rstrip("，、；; ") + "…"
        truncated = True

    if style == "更有感染力":
        result_text += f"\n\n说到底，{data['keep'] or '把想法真正做出来'}，才是这件事最值得期待的部分。"

    notes = [
        f"- 风格：{style}；强度：{strength}，共处理 {min(limit, len(sentences))}/{len(sentences)} 个句子。",
        f"- 必须保留：{data['keep'] or '原文核心信息'}。",
        f"- 字数：由 {len(source)} 字调整为 {len(result_text)} 字"
        + ("（已按长度上限截断）。" if truncated else "。"),
    ]
    return "\n".join([
        "改写结果",
        result_text,
        "",
        "改写说明",
        *notes,
    ])


def mock_text(tool: str, data: dict) -> str:
    if tool == "name":
        return _mock_name(data)
    if tool == "copy":
        return _mock_copy(data)
    if tool == "rewrite":
        return _mock_rewrite(data)
    return "示例模式暂不支持该工具。"


# ---------------- 图片类 ----------------

PALETTES = [
    ((250, 244, 232), (227, 91, 45), (23, 26, 31)),
    ((15, 40, 56), (24, 178, 160), (236, 245, 240)),
    ((244, 235, 220), (217, 154, 23), (30, 33, 36)),
    ((28, 27, 45), (139, 122, 255), (245, 242, 255)),
    ((233, 240, 233), (15, 118, 110), (20, 40, 35)),
]


def _wrap(text: str, width: int, max_lines: int) -> list:
    lines = textwrap.wrap(text, width=width) or [text]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(1, width - 1)] + "…"
    return lines


def _svg(size: str, prompt: str, style: str, index: int) -> str:
    width, height = (int(part) for part in size.lower().split("x"))
    background, accent, ink = PALETTES[index % len(PALETTES)]
    title_size = max(24, width // 22)
    body_size = max(16, width // 42)
    label_size = max(11, width // 78)
    lines = _wrap(prompt, 16 if width >= height else 12, 4)
    line_height = int(body_size * 1.6)
    text_block_height = line_height * len(lines)
    start_y = height // 2 - text_block_height // 2 + line_height
    prompt_svg = "".join(
        f'<text x="{width // 12}" y="{start_y + i * line_height}" '
        f'font-size="{body_size}" fill="{_rgb(ink)}" opacity="0.92">{html.escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{_rgb(background)}"/>
      <stop offset="100%" stop-color="{_rgb(accent)}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.75" cy="0.2" r="0.7">
      <stop offset="0%" stop-color="{_rgb(ink)}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="{_rgb(ink)}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bg)"/>
  <rect width="{width}" height="{height}" fill="url(#glow)"/>
  <circle cx="{int(width * 0.78)}" cy="{int(height * 0.28)}" r="{int(min(width, height) * 0.18)}" fill="{_rgb(ink)}" opacity="0.16"/>
  <circle cx="{int(width * 0.2)}" cy="{int(height * 0.82)}" r="{int(min(width, height) * 0.26)}" fill="{_rgb(background)}" opacity="0.5"/>
  <rect x="{width // 24}" y="{height // 24}" width="{width - width // 12}" height="{height - height // 12}" fill="none" stroke="{_rgb(ink)}" stroke-opacity="0.5" stroke-width="2"/>
  <text x="{width // 12}" y="{height // 5}" font-size="{label_size}" letter-spacing="4" fill="{_rgb(ink)}" opacity="0.75" font-family="monospace">AI CREATIVE WORKSHOP</text>
  <text x="{width // 12}" y="{int(height * 0.42)}" font-size="{title_size}" font-weight="700" fill="{_rgb(ink)}" font-family="sans-serif">{html.escape(style)}</text>
  {prompt_svg}
  <text x="{width // 12}" y="{height - height // 12}" font-size="{label_size}" fill="{_rgb(ink)}" opacity="0.8" font-family="monospace">示例占位图 / MOCK PREVIEW</text>
</svg>"""


def _rgb(triplet) -> str:
    return f"rgb({triplet[0]},{triplet[1]},{triplet[2]})"


def mock_images(prompt: str, style: str, size: str, count: int) -> list:
    images = []
    for index in range(count):
        svg = _svg(size, prompt, style, index)
        encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        images.append(f"data:image/svg+xml;base64,{encoded}")
    return images
