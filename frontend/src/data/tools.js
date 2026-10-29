const options = (...values) =>
  values.map((value) => (typeof value === 'string' ? { value, label: value } : value))

const STYLE_OPTIONS = options('创意', '稳重', '国潮', '科技', '可爱')
const PLATFORM_OPTIONS = options('公众号', '小红书', '短视频', '海报', '通用')
const LENGTH_OPTIONS = options('短', '中', '长')
const REWRITE_STYLE_OPTIONS = options('更口语', '更正式', '更简洁', '更有感染力')
const STRENGTH_OPTIONS = options('轻度', '中度', '深度')
const IMAGE_STYLE_OPTIONS = options('写实摄影', '电影感', '扁平插画', '3D 渲染', '水彩', '国潮插画', '像素风')
const IMAGE_SIZE_OPTIONS = [
  { value: '1024x1024', label: '1:1 方形 · 1024×1024' },
  { value: '1536x1024', label: '4:3 横版 · 1536×1024' },
  { value: '1024x1536', label: '3:4 竖版 · 1024×1536' }
]

export const tools = [
  {
    key: 'name',
    title: '起名工具',
    nav: '起名',
    path: '/tools/name',
    accent: 'coral',
    glyph: 'spark',
    tagline: '给品牌、社团、产品起个记得住的名字',
    description: '输入行业、关键词与风格，批量得到候选名称、寓意与可执行的使用建议。',
    modelType: 'text',
    resultLabel: '命名方案',
    examples: [
      {
        label: '校园咖啡品牌',
        values: { industry: '校园咖啡品牌', keywords: '手冲、自习、温暖', style: '国潮', count: 6, avoid: '生僻字', extra: '面向 18-22 岁学生，希望带一点校园记忆' }
      },
      {
        label: 'AI 社团',
        values: { industry: '校园 AI 社团', keywords: '创意、开放、动手', style: '科技', count: 8, avoid: '', extra: '需要能延展出一系列活动名' }
      },
      {
        label: '读书类 App',
        values: { industry: '读书类 App', keywords: '专注、轻量、陪伴', style: '创意', count: 6, avoid: '书、读', extra: '名字要适合做图标' }
      }
    ],
    fields: [
      { key: 'industry', label: '行业 / 领域', type: 'text', placeholder: '如：校园咖啡品牌、AI 社团、学习类 App', required: true, maxlength: 40, hint: '一句话说明你要命名的是什么' },
      { key: 'keywords', label: '关键词', type: 'text', placeholder: '如：手冲、自习、温暖', maxlength: 80, hint: '用顿号或逗号分隔' },
      { key: 'style', label: '风格', type: 'select', options: STYLE_OPTIONS, default: '创意' },
      { key: 'count', label: '数量', type: 'number', min: 1, max: 12, default: 6, hint: '1-12 个' },
      { key: 'avoid', label: '避用词', type: 'text', placeholder: '如：生僻字、已有品牌名', maxlength: 60 },
      { key: 'extra', label: '补充说明', type: 'textarea', rows: 2, maxlength: 300, span: 2, placeholder: '如：希望包含地名，或面向 18-22 岁人群' }
    ]
  },
  {
    key: 'copy',
    title: '文案生成',
    nav: '文案',
    path: '/tools/copy',
    accent: 'teal',
    glyph: 'pen',
    tagline: '把想法写成能直接发布的文案',
    description: '按平台结构生成标题、正文与话题标签，小红书、公众号、短视频、海报都能用。',
    modelType: 'text',
    resultLabel: '文案草稿',
    examples: [
      {
        label: '小红书 · 读书会招募',
        values: { platform: '小红书', topic: '校园读书会招募', audience: '大学生', tone: '亲切', length: '中', selling_points: '每周一次共读、零门槛参与、提供精选书单', extra: '不要夸张营销词' }
      },
      {
        label: '公众号 · 协会招新',
        values: { platform: '公众号', topic: '协会年度招新', audience: '大一新生', tone: '真诚克制', length: '长', selling_points: '真实项目经历、学长学姐带教、参与时间灵活', extra: '结尾放报名方式占位' }
      },
      {
        label: '短视频 · AI 绘画科普',
        values: { platform: '短视频', topic: '三分钟讲清 AI 绘画', audience: '对 AI 好奇的同学', tone: '轻快', length: '短', selling_points: '零基础可上手、现场演示、免费工具清单', extra: '适合竖屏口播' }
      }
    ],
    fields: [
      { key: 'platform', label: '使用平台', type: 'select', options: PLATFORM_OPTIONS, default: '通用' },
      { key: 'topic', label: '产品 / 主题', type: 'text', placeholder: '如：校园读书会招募', required: true, maxlength: 120 },
      { key: 'audience', label: '目标受众', type: 'text', placeholder: '如：大一新生、周边上班族', maxlength: 60 },
      { key: 'tone', label: '语气', type: 'text', placeholder: '如：亲切、专业克制、轻快', maxlength: 30, default: '亲切自然' },
      { key: 'length', label: '长度', type: 'select', options: LENGTH_OPTIONS, default: '中' },
      { key: 'selling_points', label: '核心卖点', type: 'textarea', rows: 3, maxlength: 300, span: 2, placeholder: '用顿号分隔，如：每周一次共读、零门槛参与、提供书单' },
      { key: 'extra', label: '补充要求', type: 'textarea', rows: 2, maxlength: 300, span: 2, placeholder: '如：避免夸张营销词，结尾放报名方式' }
    ]
  },
  {
    key: 'rewrite',
    title: '内容改写',
    nav: '改写',
    path: '/tools/rewrite',
    accent: 'violet',
    glyph: 'swap',
    tagline: '同一段话，换个语气再说一遍',
    description: '口语、正式、精简、感染力四种方向，保留关键信息与事实，不改原意。',
    modelType: 'text',
    resultLabel: '改写结果',
    examples: [
      {
        label: '活动通知改口语',
        values: {
          source: '为进一步提升校园文化氛围，丰富同学们的课余生活，经研究决定，将于本月举办创意市集活动。活动报名通道现已开启，请有意参与的同学于本周五前完成线上报名，逾期将不再受理。',
          style: '更口语',
          strength: '中度',
          keep: '活动名称、报名截止时间',
          length_limit: ''
        }
      },
      {
        label: '长文精简',
        values: {
          source: '本次工作坊将围绕人工智能工具在校园场景中的实际应用展开，内容包括提示词设计、内容生成流程、常见误区与风险提示等。活动时间为本周四晚七点，地点为图书馆三楼创客空间。由于场地容量有限，本次活动限额四十人，需要提前报名。报名成功后请准时参加，如无法到场请提前一天在小程序中取消，以便把名额留给其他同学。',
          style: '更简洁',
          strength: '深度',
          keep: '活动时间、地点、限额、取消规则',
          length_limit: 120
        }
      },
      {
        label: '口语改正式',
        values: {
          source: '咱们这周要搞个分享会，想来的同学在群里接龙一下，人差不多就够了，到时候记得别迟到哈。',
          style: '更正式',
          strength: '中度',
          keep: '分享会时间、报名方式',
          length_limit: ''
        }
      }
    ],
    fields: [
      { key: 'source', label: '原文', type: 'textarea', rows: 9, required: true, minlength: 10, maxlength: 2000, span: 2, placeholder: '粘贴需要改写的原文，10-2000 字' },
      { key: 'style', label: '改写风格', type: 'select', options: REWRITE_STYLE_OPTIONS, default: '更口语' },
      { key: 'strength', label: '改写强度', type: 'select', options: STRENGTH_OPTIONS, default: '中度' },
      { key: 'keep', label: '必须保留要点', type: 'text', maxlength: 200, placeholder: '如：时间、地点、报名方式' },
      { key: 'length_limit', label: '长度限制', type: 'number', min: 50, max: 2000, placeholder: '留空表示不限制', hint: '字数上限，50-2000' }
    ]
  },
  {
    key: 'image',
    title: '图片生成',
    nav: '图片',
    path: '/tools/image',
    accent: 'amber',
    glyph: 'frame',
    tagline: '把画面描述变成可用的概念图',
    description: '描述画面、风格与比例，生成配图灵感。演示模式会用本地占位图代替，不消耗第三方额度。',
    modelType: 'image',
    resultLabel: '图片结果',
    examples: [
      {
        label: '电影感校园夜景',
        values: { prompt: '雨后的校园天台，远处城市灯火，一个人背着包望向远方，低机位广角', style: '电影感', size: '1536x1024', count: 1, negative: '文字、水印、畸形手部、过曝' }
      },
      {
        label: '扁平插画海报',
        values: { prompt: 'AI 创意工坊招新海报，齿轮与画笔交织，几个人围坐讨论，明亮配色，上方留白', style: '扁平插画', size: '1024x1536', count: 2, negative: '真实照片质感、杂乱背景、文字' }
      },
      {
        label: '产品概念图',
        values: { prompt: '一款极简白色桌面音箱，柔和晨光，木质桌面，产品特写', style: '写实摄影', size: '1024x1024', count: 1, negative: 'logo、文字、复杂背景' }
      }
    ],
    fields: [
      { key: 'prompt', label: '画面描述', type: 'textarea', rows: 4, required: true, minlength: 2, maxlength: 500, span: 2, placeholder: '描述主体、场景、光线与构图，如：雨后的校园天台，远处灯火，低机位广角' },
      { key: 'style', label: '风格', type: 'select', options: IMAGE_STYLE_OPTIONS, default: '电影感' },
      { key: 'size', label: '尺寸 / 比例', type: 'select', options: IMAGE_SIZE_OPTIONS, default: '1024x1024' },
      { key: 'count', label: '数量', type: 'select', options: options('1', '2', '3', '4'), default: '1' },
      { key: 'negative', label: '负面提示词', type: 'textarea', rows: 2, maxlength: 200, span: 2, placeholder: '如：文字、水印、低质量、畸形手部' }
    ]
  }
]

export const toolByKey = Object.fromEntries(tools.map((tool) => [tool.key, tool]))

export function getTool(key) {
  return toolByKey[key] || null
}

export function defaultValues(tool) {
  const values = {}
  for (const field of tool.fields) {
    if (field.default !== undefined) {
      values[field.key] = field.default
    } else if (field.type === 'select') {
      values[field.key] = field.options?.[0]?.value ?? ''
    } else if (field.type === 'number') {
      values[field.key] = ''
    } else {
      values[field.key] = ''
    }
  }
  return values
}

export function validateForm(tool, values) {
  const errors = {}
  for (const field of tool.fields) {
    const raw = values[field.key]
    const text = String(raw ?? '').trim()

    if (field.required && !text) {
      errors[field.key] = `请填写「${field.label}」`
      continue
    }
    if (!text) continue
    if (field.minlength && text.length < field.minlength) {
      errors[field.key] = `「${field.label}」至少 ${field.minlength} 个字符`
      continue
    }
    if (field.maxlength && text.length > field.maxlength) {
      errors[field.key] = `「${field.label}」最多 ${field.maxlength} 个字符`
      continue
    }
    if (field.type === 'number') {
      const num = Number(text)
      if (Number.isNaN(num)) {
        errors[field.key] = `「${field.label}」必须是数字`
      } else if (field.min !== undefined && num < field.min) {
        errors[field.key] = `「${field.label}」不能小于 ${field.min}`
      } else if (field.max !== undefined && num > field.max) {
        errors[field.key] = `「${field.label}」不能大于 ${field.max}`
      }
    }
  }
  return errors
}

const SUMMARY_FIELDS = {
  name: ['industry', 'style'],
  copy: ['topic', 'platform'],
  rewrite: ['style', 'strength'],
  image: ['prompt', 'style']
}

export function summarizeInput(tool, values) {
  const keys = SUMMARY_FIELDS[tool.key] || []
  const parts = keys
    .map((key) => String(values[key] ?? '').trim())
    .filter(Boolean)
  const text = parts.join(' · ')
  return text.length > 120 ? `${text.slice(0, 120)}…` : text
}
