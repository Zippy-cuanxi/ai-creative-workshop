const NAME_PREFIX = {
  创意: [
    ['浮光', '取光线的流动感，轻盈、有想象空间'],
    ['奇点', '象征创意爆发的起点'],
    ['半野', '介于规整与自由之间，保留野生感'],
    ['未迟', '一切都还来得及，带有少年气'],
    ['回声', '强调被听见、被回应'],
    ['小满', '恰到好处，留有余地'],
    ['拾光', '把零散的好时光收起来'],
    ['无界', '不设边界，主打开放与跨界']
  ],
  稳重: [
    ['正和', '取正道与和气，稳妥可信'],
    ['恒远', '强调长期主义与持续经营'],
    ['厚德', '取自厚德载物，突出责任感'],
    ['中衡', '强调平衡与专业判断'],
    ['同源', '强调共同来源与协作'],
    ['久成', '长久积累，自然成事'],
    ['立言', '取立言立行，重承诺'],
    ['清和', '清爽平和，不张扬']
  ],
  国潮: [
    ['山河', '把地理与家国气韵写进名字'],
    ['青瓷', '取自宋代青瓷，温润克制'],
    ['见山', '取自见山是山，留白有意境'],
    ['归鹤', '仙鹤归巢，带东方浪漫'],
    ['云锦', '取织锦之意，华而不艳'],
    ['拾遗', '打捞被忽略的传统细节'],
    ['松间', '取自松间明月，清雅安静'],
    ['渡口', '有出发与相遇的画面感']
  ],
  科技: [
    ['矩阵', '强调结构与秩序感'],
    ['量子', '代表微小却关键的跃迁'],
    ['原点', '一切从这里开始'],
    ['星链', '连接成网，指向未来'],
    ['智核', '把智能放进内核'],
    ['极简', '少即是多，效率优先'],
    ['深蓝', '冷静、专业、可信'],
    ['脉冲', '短促有力，强调节奏']
  ],
  可爱: [
    ['团子', '软糯圆润，亲和力强'],
    ['软糖', '甜而不腻，记忆点强'],
    ['布丁', 'Q 弹可爱，适合年轻客群'],
    ['喵吉', '带一点小动物式的俏皮'],
    ['小鹿', '清澈、灵动、不具攻击性'],
    ['圆圆', '形状感强，适合做视觉符号'],
    ['豆丁', '小巧亲切，口语传播成本低'],
    ['阿满', '像朋友的小名，容易亲近']
  ]
}

const TOOL_SUFFIX = {
  社团: ['社', '共创社', '青年社'],
  协会: ['协会', '联盟', '工坊'],
  咖啡: ['工坊', '小馆', '食集'],
  茶: ['茶舍', '小馆', '工坊'],
  烘焙: ['烘焙所', '食集', '工坊'],
  品牌: ['品牌', '实验室', '计划'],
  课程: ['课堂', '研习社', '计划'],
  活动: ['计划', '企划', '现场']
}

const COLLOQUIAL_MAP = [
  ['因此', '所以'], ['以及', '还有'], ['进行', '做'], ['是否', '是不是'],
  ['如需', '要是想'], ['此外', '另外'], ['目前', '现在'], ['较为', '挺'],
  ['显著', '很明显'], ['旨在', '主要是想'], ['通过', '用'], ['具有', '有'],
  ['从而', '这样'], ['基于', '根据'], ['倘若', '如果'], ['鉴于', '考虑到'],
  ['为此', '为了这件事'], ['陆续', '一个接一个']
]

const FORMAL_MAP = [
  ['挺', '较为'], ['特别', '尤为'], ['搞', '推进'], ['咱们', '我们'],
  ['啥', '什么'], ['很多', '大量'], ['差不多', '基本'], ['不行', '不可行'],
  ['说白了', '简而言之'], ['反正', '总之'], ['挺好', '较为理想'],
  ['超级', '非常'], ['老是', '频繁'], ['弄', '处理']
]

const FILLERS = ['其实', '基本上', '真的', '非常', '十分', '的话', '就是说', '可以说', '说实话']

const PALETTES = [
  [[250, 244, 232], [227, 91, 45], [23, 26, 31]],
  [[15, 40, 56], [24, 178, 160], [236, 245, 240]],
  [[244, 235, 220], [217, 154, 23], [30, 33, 36]],
  [[28, 27, 45], [139, 122, 255], [245, 242, 255]],
  [[233, 240, 233], [15, 118, 110], [20, 40, 35]]
]

function rgb(triplet) {
  return `rgb(${triplet[0]},${triplet[1]},${triplet[2]})`
}

function splitPoints(value) {
  if (!value) return []
  return String(value)
    .split(/[、,，;；\n]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function suffixes(industry, style) {
  for (const key of Object.keys(TOOL_SUFFIX)) {
    if (industry.includes(key)) return TOOL_SUFFIX[key]
  }
  if (style === '国潮') return ['堂', '舍', '集']
  if (style === '可爱') return ['屋', '小铺', '乐园']
  if (style === '科技') return ['实验室', '引擎', '计划']
  return ['工作室', '造物', '计划', '空间']
}

function mockName(data) {
  const prefixes = NAME_PREFIX[data.style] || NAME_PREFIX['创意']
  const tools = suffixes(data.industry, data.style)
  const count = Number(data.count) || 6
  const names = []
  for (let index = 0; index < count; index += 1) {
    const [prefix, meaning] = prefixes[index % prefixes.length]
    const suffix = tools[index % tools.length]
    names.push([`${prefix}${suffix}`, meaning])
  }

  const lines = [
    '命名思路',
    `面向「${data.industry}」，以「${data.style}」为基调：前缀取 2 字意象，后缀点明品类，整体控制在 3-4 字，读音干净、便于口头传播` +
      (data.avoid ? `；同时避开「${data.avoid}」。` : '。'),
    '',
    '备选名称'
  ]
  names.forEach(([name, meaning], index) => {
    lines.push(`${index + 1}. ${name}`)
    lines.push(`   寓意：${meaning}；后缀明确指向「${data.industry}」的业务属性。`)
  })
  lines.push(
    '',
    '使用建议',
    '1. 先在目标人群中做一次口头测试，确认没有负面谐音与理解偏差。',
    '2. 名称确定后尽快做商标近似查询，并检索域名、公众号与社交账号是否可用。',
    '3. 保留 1-2 个备选名，方便后续做系列产品或活动延展。'
  )
  if (data.extra) lines.push('', `补充说明已考虑：${data.extra}`)
  return lines.join('\n')
}

function copyPoints(data) {
  const points = splitPoints(data.selling_points)
  const defaults = [
    `${data.topic}的真实使用场景`,
    '上手门槛低，第一次就能用',
    '有清楚的结果与反馈'
  ]
  while (points.length < 3) points.push(defaults[points.length])
  return points.slice(0, 4)
}

function mockCopy(data) {
  const topic = data.topic
  const audience = data.audience || '目标读者'
  const points = copyPoints(data)
  const toneLine = data.tone ? `整体语气：${data.tone}。` : ''
  let result = ''

  if (data.platform === '小红书') {
    const supportLines = [
      '真实体验是：不用准备太久，第一次就能上手，反馈也比较直接。',
      '身边同学的反馈是：门槛比想象中低，照着清单做就行。',
      '实际用下来：细节考虑得比较周到，遇到问题也有人答疑。'
    ]
    const body = [
      '标题备选',
      `1. ${topic}｜${audience}最关心的 3 个问题`,
      `2. 关于${topic}，我帮你先试了一遍`,
      '',
      '正文',
      `最近有${audience}反复问我：${topic}到底值不值得了解。我把它拆成 3 点，看完大概就有答案了。`,
      ''
    ]
    points.forEach((point, index) => {
      body.push(`${index + 1}. ${point}`)
      body.push(`   ${supportLines[index % supportLines.length]}`)
    })
    body.push(
      '',
      `如果你也在关注${topic}，建议先从最小的一步开始，不需要等到“准备好”。`,
      '',
      '话题标签',
      `#${topic.replace(/\s/g, '')} #实用分享 #新手入门 #经验总结 #${audience.replace(/\s/g, '')}`
    )
    result = body.join('\n')
  } else if (data.platform === '公众号') {
    result = [
      '标题',
      `${topic}：给${audience}的一份实用说明`,
      '',
      '导语',
      `这段时间，${topic}被反复提起。这篇文章不堆概念，只讲清楚三件事：它解决什么问题、为什么现在值得关注、以及怎么开始。`,
      '',
      '一、它解决什么问题',
      `对${audience}来说，最直接的收益是：${points[0]}。很多讨论停在名词层面，但真正的差别在于是否用起来。`,
      '',
      '二、为什么现在值得关注',
      `${points[1]}。当基础条件逐渐成熟，早一步尝试的成本会比想象中低。`,
      '',
      '三、怎么开始',
      `建议从最小的场景切入：${points[2]}。给自己设一个一周的小目标，比一次性做完整方案更容易坚持。`,
      '',
      '写在最后',
      `如果你身边也有${audience}在关注${topic}，欢迎把这篇内容转给 TA。`
    ].join('\n')
  } else if (data.platform === '短视频') {
    result = [
      '封面文案',
      `${topic}，3 个重点一次讲清`,
      '',
      '分镜脚本',
      `0-3 秒（钩子）：还在纠结${topic}？先别划走，这条讲人话。`,
      `3-12 秒（痛点）：${audience}最常见的卡点是——不知道怎么开始，也不知道做了有什么用。`,
      `12-25 秒（要点）：第一，${points[0]}；第二，${points[1]}；第三，${points[2]}。`,
      '25-35 秒（收尾）：想试试的话，先从最小的一步开始，评论区告诉我你的场景，我帮你拆。',
      '',
      '拍摄提示',
      '竖屏构图，人物居中偏左，关键词用大字幕压在画面上三分之一；每 5 秒切一次景别，避免长时间固定镜头。'
    ].join('\n')
  } else if (data.platform === '海报') {
    result = [
      '主标题',
      topic,
      '',
      '副标题',
      `给${audience}的一个新选择`,
      '',
      '利益点',
      `- ${points[0]}`,
      `- ${points[1]}`,
      `- ${points[2]}`,
      '',
      '行动按钮',
      '立即了解',
      '',
      '视觉建议',
      '主标题用粗体大字占画面 40%，利益点用 3 行短句，留出足够白边；整体控制在 3 种颜色以内。'
    ].join('\n')
  } else {
    result = [
      '标题',
      `${topic}：${audience}需要知道的三件事`,
      '',
      `开头：如果你正在关注${topic}，这条内容可以帮你快速建立判断。${toneLine}`,
      '',
      '三个重点',
      `1. ${points[0]}`,
      `2. ${points[1]}`,
      `3. ${points[2]}`,
      '',
      '结尾',
      `把${topic}放进你接下来一周的计划里，先做一个小实验，比停留在收藏夹更有效。`
    ].join('\n')
  }

  if (data.extra) result += `\n\n补充要求已处理：${data.extra}`
  return result
}

function splitSentences(text) {
  return (String(text).match(/[^。！？!?；;\n]+[。！？!?；;]?/g) || [])
    .map((item) => item.trim())
    .filter(Boolean)
}

function applyMap(text, mapping) {
  let value = text
  for (const [source, target] of mapping) {
    value = value.split(source).join(target)
  }
  return value
}

function mockRewrite(data) {
  const ratio = { 轻度: 0.35, 中度: 0.65, 深度: 1 }[data.strength] || 0.65
  const sentences = splitSentences(data.source)
  const limit = Math.min(sentences.length, Math.max(1, Math.round(ratio * sentences.length)))
  const processed = []

  sentences.forEach((sentence, index) => {
    let value = sentence
    if (index < limit) {
      if (data.style === '更口语') {
        value = applyMap(value, COLLOQUIAL_MAP)
        if (index === 0 && !value.includes('说白了')) value = `说白了，${value}`
      } else if (data.style === '更正式') {
        value = applyMap(value, FORMAL_MAP)
        if (index === 0) value = `基于上述背景，${value}`
      } else if (data.style === '更简洁') {
        for (const filler of FILLERS) value = value.split(filler).join('')
      } else if (data.style === '更有感染力') {
        if (index === 0) value = `如果把这件事讲得更直白一点：${value}`
        else if (index === 1) value = `你可以想象一下：${value}`
      }
    }
    if (value.trim()) processed.push(value)
  })

  let resultText = processed.join('')
  const lengthLimit = Number(data.length_limit) || 0
  let truncated = false
  if (lengthLimit && resultText.length > lengthLimit) {
    resultText = `${resultText.slice(0, lengthLimit).replace(/[，、；; ]+$/, '')}…`
    truncated = true
  }
  if (data.style === '更有感染力') {
    resultText += `\n\n说到底，${data.keep || '把想法真正做出来'}，才是这件事最值得期待的部分。`
  }

  return [
    '改写结果',
    resultText,
    '',
    '改写说明',
    `- 风格：${data.style}；强度：${data.strength}，共处理 ${limit}/${sentences.length} 个句子。`,
    `- 必须保留：${data.keep || '原文核心信息'}。`,
    `- 字数：由 ${String(data.source).length} 字调整为 ${resultText.length} 字${truncated ? '（已按长度上限截断）。' : '。'}`
  ].join('\n')
}

function wrapText(text, width, maxLines) {
  const chars = Array.from(text)
  const lines = []
  for (let index = 0; index < chars.length; index += width) {
    lines.push(chars.slice(index, index + width).join(''))
    if (lines.length >= maxLines) break
  }
  if (!lines.length) lines.push(text)
  if (chars.length > width * maxLines) {
    lines[maxLines - 1] = `${lines[maxLines - 1].slice(0, width - 1)}…`
  }
  return lines
}

function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function makeSvg(size, prompt, style, index) {
  const [width, height] = String(size).toLowerCase().split('x').map(Number)
  const [background, accent, ink] = PALETTES[index % PALETTES.length]
  const titleSize = Math.max(24, Math.floor(width / 22))
  const bodySize = Math.max(16, Math.floor(width / 42))
  const labelSize = Math.max(11, Math.floor(width / 78))
  const lines = wrapText(prompt, width >= height ? 16 : 12, 4)
  const lineHeight = Math.floor(bodySize * 1.6)
  const textBlockHeight = lineHeight * lines.length
  const startY = Math.floor(height / 2 - textBlockHeight / 2 + lineHeight)
  const promptSvg = lines
    .map(
      (line, i) =>
        `<text x="${Math.floor(width / 12)}" y="${startY + i * lineHeight}" font-size="${bodySize}" fill="${rgb(ink)}" opacity="0.92">${escapeXml(line)}</text>`
    )
    .join('')
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${rgb(background)}"/>
      <stop offset="100%" stop-color="${rgb(accent)}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.75" cy="0.2" r="0.7">
      <stop offset="0%" stop-color="${rgb(ink)}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="${rgb(ink)}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="${width}" height="${height}" fill="url(#bg)"/>
  <rect width="${width}" height="${height}" fill="url(#glow)"/>
  <circle cx="${Math.floor(width * 0.78)}" cy="${Math.floor(height * 0.28)}" r="${Math.floor(Math.min(width, height) * 0.18)}" fill="${rgb(ink)}" opacity="0.16"/>
  <circle cx="${Math.floor(width * 0.2)}" cy="${Math.floor(height * 0.82)}" r="${Math.floor(Math.min(width, height) * 0.26)}" fill="${rgb(background)}" opacity="0.5"/>
  <rect x="${Math.floor(width / 24)}" y="${Math.floor(height / 24)}" width="${width - Math.floor(width / 12)}" height="${height - Math.floor(height / 12)}" fill="none" stroke="${rgb(ink)}" stroke-opacity="0.5" stroke-width="2"/>
  <text x="${Math.floor(width / 12)}" y="${Math.floor(height / 5)}" font-size="${labelSize}" letter-spacing="4" fill="${rgb(ink)}" opacity="0.75" font-family="monospace">AI CREATIVE WORKSHOP</text>
  <text x="${Math.floor(width / 12)}" y="${Math.floor(height * 0.42)}" font-size="${titleSize}" font-weight="700" fill="${rgb(ink)}" font-family="sans-serif">${escapeXml(style)}</text>
  ${promptSvg}
  <text x="${Math.floor(width / 12)}" y="${height - Math.floor(height / 12)}" font-size="${labelSize}" fill="${rgb(ink)}" opacity="0.8" font-family="monospace">静态演示图 / MOCK PREVIEW</text>
</svg>`
}

function svgToDataUri(svg) {
  const bytes = new TextEncoder().encode(svg)
  let binary = ''
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index])
  }
  return `data:image/svg+xml;base64,${btoa(binary)}`
}

export function generateLocal(tool, input) {
  if (tool === 'name') return { type: 'text', text: mockName(input), images: [] }
  if (tool === 'copy') return { type: 'text', text: mockCopy(input), images: [] }
  if (tool === 'rewrite') return { type: 'text', text: mockRewrite(input), images: [] }
  const count = Number(input.count) || 1
  const images = []
  for (let index = 0; index < count; index += 1) {
    images.push(svgToDataUri(makeSvg(input.size, input.prompt, input.style, index)))
  }
  return { type: 'image', text: '', images }
}
