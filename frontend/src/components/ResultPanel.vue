<script setup>
import { computed } from 'vue'

import { useToast } from '../composables/useToast'
import { copyText } from '../utils/clipboard'
import { formatDuration } from '../utils/format'
import ToolGlyph from './ToolGlyph.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  result: { type: Object, default: null },
  error: { type: Object, default: null },
  requestId: { type: String, default: '' },
  remaining: { type: Object, default: null },
  latency: { type: Number, default: 0 },
  modelLabel: { type: String, default: '' },
  toolTitle: { type: String, default: '' },
  savedId: { type: String, default: '' },
  imageAlt: { type: String, default: '' }
})

const emit = defineEmits(['retry', 'regenerate'])
const toast = useToast()

const isText = computed(() => props.result && props.result.type === 'text')
const images = computed(() => (props.result && props.result.images) || [])
const latencyLabel = computed(() => {
  if (!props.latency) return ''
  return props.latency < 1000 ? `${props.latency} ms` : `${(props.latency / 1000).toFixed(1)} s`
})

function downloadName(index) {
  const raw = images.value[index] || ''
  let ext = 'png'
  if (raw.startsWith('data:image/svg')) ext = 'svg'
  else if (raw.includes('.jpg') || raw.includes('jpeg')) ext = 'jpg'
  else if (!raw.startsWith('data:image/png')) ext = 'jpg'
  return `ai-workshop-${Date.now()}-${index + 1}.${ext}`
}

function isRemote(url) {
  return /^https?:\/\//i.test(url)
}

async function copyResult() {
  const ok = await copyText((props.result && props.result.text) || '')
  if (ok) toast.success('结果已复制到剪贴板')
  else toast.error('复制失败，请手动选择文本')
}

async function copyImageLink(index) {
  const ok = await copyText(images.value[index] || '')
  if (ok) toast.success('图片链接已复制')
  else toast.error('复制失败')
}
</script>

<template>
  <section class="card panel tool-result" aria-label="生成结果">
    <div class="panel-head">
      <h2 class="panel-title"><span class="panel-title__dot" aria-hidden="true"></span>生成结果</h2>
      <span v-if="result && result.mock" class="badge">示例模式</span>
    </div>

    <div class="sr-only" aria-live="polite">
      {{ loading ? '正在生成，请稍候' : result ? '生成完成' : '' }}
    </div>

    <div v-if="loading" class="loading-block" role="status" aria-live="polite">
      <div class="skeleton skeleton--title"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton skeleton--short"></div>
      <div class="skeleton skeleton--short"></div>
      <p class="loading-note"><span class="spinner" aria-hidden="true"></span>模型正在思考，通常需要几秒到几十秒。</p>
    </div>

    <div v-else-if="error" class="error-box" role="alert">
      <div class="error-box__title">
        生成失败
        <span class="mono">· {{ error.code }}</span>
      </div>
      <p class="error-box__message">{{ error.message }}</p>
      <p v-if="error.retryAfter" class="hint">
        预计 {{ formatDuration(error.retryAfter) }}后恢复，请先看看模板库。
      </p>
      <p v-if="requestId" class="error-box__meta">request_id：{{ requestId }}</p>
      <div class="result-actions">
        <button type="button" class="btn btn-sm btn-primary" @click="emit('retry')">重试一次</button>
        <RouterLink to="/about" class="btn btn-sm btn-ghost">查看限流与风险说明</RouterLink>
      </div>
    </div>

    <div v-else-if="result" class="result-card">
      <template v-if="isText">
        <pre class="result-text">{{ result.text }}</pre>
        <div class="result-actions">
          <button type="button" class="btn btn-sm" @click="copyResult">复制结果</button>
          <button type="button" class="btn btn-sm btn-ghost" @click="emit('regenerate')">重新生成</button>
        </div>
      </template>

      <template v-else>
        <div class="image-grid">
          <figure v-for="(image, index) in images" :key="index" class="image-card">
            <img
              :src="image"
              :alt="`${toolTitle}生成的第 ${index + 1} 张图片${imageAlt ? '：' + imageAlt : ''}`"
              loading="lazy"
            />
            <figcaption>
              <span>第 {{ index + 1 }} 张</span>
              <span style="display: flex; gap: 8px">
                <button type="button" class="btn-quiet" @click="copyImageLink(index)">复制链接</button>
                <a :href="image" :download="downloadName(index)" :target="isRemote(image) ? '_blank' : undefined" :rel="isRemote(image) ? 'noopener' : undefined">下载</a>
              </span>
            </figcaption>
          </figure>
        </div>
        <div class="result-actions">
          <button type="button" class="btn btn-sm btn-ghost" @click="emit('regenerate')">重新生成</button>
        </div>
        <p v-if="result.mock" class="hint">演示模式的图片为本地 SVG 占位图；接入真实图像 API 后会返回实际生成结果。</p>
      </template>

      <div v-if="savedId" class="saved-note">
        <span>已自动保存到本地历史</span>
        <RouterLink to="/history">查看历史</RouterLink>
      </div>

      <div class="result-meta">
        <div class="result-meta__row">
          <span>request_id：{{ requestId || '—' }}</span>
        </div>
        <div class="result-meta__row">
          <span>模型：{{ modelLabel || '—' }}</span>
          <span v-if="latency">耗时：{{ latencyLabel }}</span>
        </div>
        <div v-if="remaining" class="result-meta__row">
          <span>今日剩余 {{ remaining.dayRemaining }} 次</span>
          <span>本分钟剩余 {{ remaining.minuteRemaining }} 次</span>
        </div>
      </div>
    </div>

    <div v-else class="result-empty">
      <span class="result-empty__icon"><ToolGlyph name="spark" :size="22" /></span>
      <span class="result-empty__title">这里会显示生成结果</span>
      <span class="result-empty__text">
        填写左侧需求或点击快速示例，生成后可复制、重新生成，结果会自动保存到本地历史。
      </span>
    </div>
  </section>
</template>
