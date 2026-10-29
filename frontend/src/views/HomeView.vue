<script setup>
import { computed, onMounted } from 'vue'

import RiskBanner from '../components/RiskBanner.vue'
import TemplateCard from '../components/TemplateCard.vue'
import ToolCard from '../components/ToolCard.vue'
import { toolByKey, tools } from '../data/tools'
import { useHistoryStore } from '../stores/history'
import { useTemplatesStore } from '../stores/templates'
import { formatDateTime } from '../utils/format'

const templateStore = useTemplatesStore()
const historyStore = useHistoryStore()

onMounted(() => {
  templateStore.load()
  historyStore.load()
})

const recommended = computed(() => {
  const hot = templateStore.items.filter((item) => item.hot)
  const rest = templateStore.items.filter((item) => !item.hot)
  return [...hot, ...rest].slice(0, 3)
})

const recent = computed(() => historyStore.records.slice(0, 3))

const templateCount = computed(() => templateStore.items.length || 13)

const riskItems = [
  {
    title: '第三方额度风险',
    text: '模型调用依赖第三方 API，可能遇到延迟、限流、额度耗尽或价格调整，站点会给出可读错误并允许重试。'
  },
  {
    title: '限流与匿名',
    text: '无需登录，使用匿名 ID + 网络哈希做限流。超限返回 429 并提示恢复时间，避免被个别访客占满额度。'
  },
  {
    title: '内容安全',
    text: '服务端会做基础敏感词拦截，上游模型也有安全审核。生成内容仅供参考，请勿用于违法或侵权用途。'
  },
  {
    title: '后端偏薄',
    text: 'Django 只做密钥保护、转发、限流与调用记录，不做账号体系与计费，复杂需求需要自行扩展。'
  }
]
</script>

<template>
  <div class="container stack">
    <RiskBanner />

    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <span class="eyebrow">公开体验 · 免登录</span>
        <h1 id="hero-title" class="hero-title">
          把想法丢进工坊，<br />带一个<span class="highlight">能用的结果</span>走。
        </h1>
        <p class="hero-lead">
          起名、文案、改写、图片，四个小工具覆盖从灵感到交付的最后一步。
          选工具、填需求、生成、复制，不需要注册，也不会上传账号信息。
        </p>
        <div class="hero-actions">
          <RouterLink to="/tools/name" class="btn btn-primary">开始体验</RouterLink>
          <RouterLink to="/templates" class="btn btn-ghost">浏览模板库</RouterLink>
        </div>
        <div class="hero-stats">
          <span><strong>4</strong>个工具</span>
          <span><strong>{{ templateCount }}</strong>套模板</span>
          <span><strong>0</strong>步注册</span>
          <span><strong>50</strong>条本地历史</span>
        </div>
      </div>

      <div class="hero-board" aria-hidden="true">
        <span class="board-tape">WORK IN PROGRESS</span>
        <span class="board-spark">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
            <path d="M12 3l2 5.6L20 11l-6 2.4L12 19l-2-5.6L4 11l6-2.4z" />
          </svg>
        </span>

        <div class="board-card board-card--prompt">
          <div class="board-card__label">
            <span>Prompt</span>
            <span>01</span>
          </div>
          <div class="board-line is-accent" style="width: 78%"></div>
          <div class="board-line"></div>
          <div class="board-line"></div>
          <div class="board-line is-short"></div>
          <div class="board-line" style="width: 42%"></div>
        </div>

        <div class="board-card board-card--result">
          <div class="board-card__label">
            <span>Result</span>
            <span>READY</span>
          </div>
          <p class="board-result-title">山岚手作</p>
          <p class="board-result-text">取山间雾气与手作温度，适合校园咖啡与烘焙空间。</p>
          <div class="board-line is-accent" style="width: 46%"></div>
        </div>

        <div class="board-swatches">
          <span class="board-swatch" style="background: #c2410c"></span>
          <span class="board-swatch" style="background: #11695f"></span>
          <span class="board-swatch" style="background: #f7ebd2"></span>
          <span class="board-swatch" style="background: #1b1b1f"></span>
        </div>
      </div>
    </section>

    <section id="tools" aria-labelledby="tools-title">
      <div class="section-head">
        <div>
          <span class="eyebrow">Tools</span>
          <h2 id="tools-title" class="section-title">四个工具，覆盖从命名到出图</h2>
          <p class="section-lead">每个工具都内置示例与模板，第一次来也能直接生成。</p>
        </div>
        <RouterLink to="/templates" class="btn btn-sm btn-ghost">模板库</RouterLink>
      </div>
      <div class="tool-grid">
        <ToolCard
          v-for="(tool, index) in tools"
          :key="tool.key"
          :tool="tool"
          :index="index + 1"
        />
      </div>
    </section>

    <section aria-labelledby="templates-title">
      <div class="section-head">
        <div>
          <span class="eyebrow">Templates</span>
          <h2 id="templates-title" class="section-title">推荐 Prompt 模板</h2>
          <p class="section-lead">选一个模板自动填充字段，再按自己的场景改两处就能用。</p>
        </div>
        <RouterLink to="/templates" class="btn btn-sm btn-ghost">查看全部</RouterLink>
      </div>
      <div v-if="recommended.length" class="template-grid">
        <TemplateCard
          v-for="template in recommended"
          :key="template.id"
          :template="template"
        />
      </div>
      <div v-else class="empty-state">
        <p class="empty-state__title">模板正在加载</p>
        <p class="empty-state__text">稍等片刻，或直接进入工具填写需求。</p>
      </div>
    </section>

    <section aria-labelledby="recent-title">
      <div class="section-head">
        <div>
          <span class="eyebrow">History</span>
          <h2 id="recent-title" class="section-title">最近生成</h2>
          <p class="section-lead">记录只保存在当前浏览器，最多保留 50 条。</p>
        </div>
        <RouterLink to="/history" class="btn btn-sm btn-ghost">全部历史</RouterLink>
      </div>

      <ul v-if="recent.length" class="recent-list card">
        <li v-for="record in recent" :key="record.id" class="recent-item">
          <span class="chip">{{ toolByKey[record.tool]?.nav || record.tool }}</span>
          <div class="recent-item__main">
            <p class="recent-item__summary">{{ record.inputSummary || '未填写摘要' }}</p>
            <p class="recent-item__meta">
              {{ formatDateTime(record.createdAt) }} · {{ record.modelName || record.model }}
            </p>
          </div>
          <RouterLink to="/history" class="btn-quiet">查看</RouterLink>
        </li>
      </ul>

      <div v-else class="empty-state">
        <p class="empty-state__title">还没有生成记录</p>
        <p class="empty-state__text">从任意工具生成一次，结果会自动保存在这里。</p>
        <RouterLink to="/tools/name" class="btn btn-sm btn-primary">先起个名字</RouterLink>
      </div>
    </section>

    <section aria-labelledby="risk-title">
      <div class="section-head">
        <div>
          <span class="eyebrow">Transparency</span>
          <h2 id="risk-title" class="section-title">先把风险说清楚</h2>
          <p class="section-lead">这是一个公开体验站点，稳定性与额度取决于第三方服务。</p>
        </div>
        <RouterLink to="/about" class="btn btn-sm btn-ghost">关于与风险</RouterLink>
      </div>
      <div class="tool-grid">
        <article v-for="item in riskItems" :key="item.title" class="card card-pad info-card">
          <h3 class="info-card__title">{{ item.title }}</h3>
          <p class="info-card__text">{{ item.text }}</p>
        </article>
      </div>
    </section>
  </div>
</template>
