<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api/client'
import ResultPanel from '../components/ResultPanel.vue'
import ToolForm from '../components/ToolForm.vue'
import ToolGlyph from '../components/ToolGlyph.vue'
import { useToast } from '../composables/useToast'
import { defaultValues, summarizeInput, toolByKey, validateForm } from '../data/tools'
import { useAppStore } from '../stores/app'
import { useHistoryStore } from '../stores/history'
import { useTemplatesStore } from '../stores/templates'
import { createId } from '../utils/id'

const props = defineProps({
  toolKey: { type: String, required: true }
})

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const templatesStore = useTemplatesStore()
const historyStore = useHistoryStore()
const toast = useToast()

const tool = computed(() => toolByKey[props.toolKey])
const toolTemplates = computed(() => templatesStore.forTool(props.toolKey))

const form = reactive(defaultValues(toolByKey[props.toolKey]))
const errors = reactive({})
const modelId = ref('')
const selectedTemplate = ref(null)

const loading = ref(false)
const result = ref(null)
const error = ref(null)
const requestId = ref('')
const remaining = ref(null)
const latency = ref(0)
const savedId = ref('')

const resultWrap = ref(null)

const modelsForTool = computed(() => appStore.modelsFor(tool.value.modelType))
const modelLabel = computed(() => {
  const model = appStore.modelById(modelId.value)
  return model ? model.name : ''
})

function initModel() {
  const list = modelsForTool.value
  const preferred = list.find((model) => model.id === appStore.defaultModel)
  modelId.value = (preferred || list[0])?.id || ''
}

function applyValues(values) {
  if (!values) return
  for (const key of Object.keys(form)) {
    if (Object.prototype.hasOwnProperty.call(values, key)) {
      form[key] = values[key]
    }
  }
}

function clearMessages() {
  Object.keys(errors).forEach((key) => delete errors[key])
}

function applyIncoming() {
  try {
    const raw = window.sessionStorage.getItem('acw:reuse')
    if (raw) {
      window.sessionStorage.removeItem('acw:reuse')
      const data = JSON.parse(raw)
      if (data && data.toolKey === props.toolKey) {
        applyValues(data.values)
        if (data.modelId && modelsForTool.value.some((model) => model.id === data.modelId)) {
          modelId.value = data.modelId
        }
        toast.push('已载入历史记录中的输入，可直接重新生成')
      }
    }
  } catch {
    /* 忽略损坏的本地数据 */
  }

  const templateId = route.query.template
  if (typeof templateId === 'string' && templateId) {
    const template = templatesStore.byId(templateId)
    if (template && template.tool === props.toolKey) {
      selectedTemplate.value = template
      applyValues(template.prefill)
      toast.push(`已载入模板「${template.title}」`)
    }
  }
}

function normalizeInput() {
  const payload = {}
  for (const field of tool.value.fields) {
    const raw = String(form[field.key] ?? '').trim()
    if (field.type === 'number') {
      payload[field.key] = raw === '' ? '' : Number(raw)
    } else {
      payload[field.key] = raw
    }
  }
  return payload
}

function saveRecord(data) {
  const record = historyStore.add({
    id: createId('rec_'),
    createdAt: new Date().toISOString(),
    tool: props.toolKey,
    toolTitle: tool.value.title,
    model: modelId.value,
    modelName: modelLabel.value,
    requestId: data.request_id,
    input: { ...form },
    inputSummary: summarizeInput(tool.value, form),
    resultType: data.result.type,
    text: data.result.text,
    images: data.result.images,
    status: 'ok',
    mock: data.result.mock,
    templateId: selectedTemplate.value ? selectedTemplate.value.id : ''
  })
  savedId.value = record.id
}

async function focusResultOnMobile() {
  await nextTick()
  if (window.innerWidth > 960) return
  if (!resultWrap.value) return
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  resultWrap.value.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' })
}

async function submit() {
  if (loading.value) return
  clearMessages()

  if (!modelId.value) {
    toast.error('模型尚未就绪，请刷新页面后重试')
    return
  }

  const validation = validateForm(tool.value, form)
  Object.assign(errors, validation)
  if (Object.keys(validation).length) {
    const firstKey = Object.keys(validation)[0]
    const control = document.getElementById(`field-${firstKey}`)
    if (control) control.focus()
    toast.error('请先完善表单中的必填项')
    return
  }

  loading.value = true
  error.value = null
  result.value = null
  savedId.value = ''
  requestId.value = ''
  latency.value = 0

  const payload = {
    tool: props.toolKey,
    model: modelId.value,
    anonymous_id: appStore.anonymousId,
    input: normalizeInput()
  }
  if (selectedTemplate.value) payload.template_id = selectedTemplate.value.id

  try {
    const data = await api.generate(payload)
    result.value = data.result
    requestId.value = data.request_id
    latency.value = data.latency_ms || 0
    remaining.value = data.remaining || null
    appStore.applyRemaining(data.remaining)
    saveRecord(data)
    toast.success('生成完成，已保存到本地历史')
    focusResultOnMobile()
  } catch (err) {
    error.value = {
      code: err.code,
      message: err.message,
      retryAfter: err.retryAfter
    }
    requestId.value = err.requestId || ''
    toast.error(err.message)
  } finally {
    loading.value = false
  }
}

function retry() {
  submit()
}

function regenerate() {
  submit()
}

function useExample(values) {
  applyValues(values)
  clearMessages()
  toast.push('已填充示例内容，可直接生成')
}

function removeTemplate() {
  selectedTemplate.value = null
  if (route.query.template) {
    router.replace({ path: route.path, query: {} })
  }
}

function applyTemplateById(templateId) {
  if (!templateId) {
    removeTemplate()
    return
  }
  const template = templatesStore.byId(templateId)
  if (!template || template.tool !== props.toolKey) return
  selectedTemplate.value = template
  applyValues(template.prefill)
  clearMessages()
  router.replace({ path: route.path, query: { template: templateId } })
  toast.push(`已载入模板「${template.title}」`)
}

function resetForm() {
  applyValues(defaultValues(tool.value))
  clearMessages()
  result.value = null
  error.value = null
  savedId.value = ''
  requestId.value = ''
  remaining.value = null
  latency.value = 0
  selectedTemplate.value = null
  initModel()
  if (route.query.template) {
    router.replace({ path: route.path, query: {} })
  }
  toast.push('表单已重置')
}

onMounted(async () => {
  await appStore.init()
  await templatesStore.load()
  initModel()
  applyIncoming()
})
</script>

<template>
  <div class="container">
    <section class="page-head">
      <span class="eyebrow">{{ tool.nav }} · 免登录</span>
      <div class="page-head__title-row">
        <span class="tool-glyph page-head__glyph" :class="`page-head__glyph--${tool.accent}`">
          <ToolGlyph :name="tool.glyph" :size="22" />
        </span>
        <h1 class="page-head__title">{{ tool.title }}</h1>
      </div>
      <p class="page-head__lead">{{ tool.description }}</p>
      <div class="page-head__meta">
        <span class="chip chip--dot">无需登录，匿名使用</span>
        <span class="chip">每分钟 {{ appStore.limits.perMinute }} 次</span>
        <span class="chip">每日 {{ appStore.limits.perDay }} 次</span>
        <RouterLink to="/templates" class="chip">可套用模板 {{ toolTemplates.length }} 套</RouterLink>
      </div>
    </section>

    <div class="tool-layout">
      <ToolForm
        :tool="tool"
        :values="form"
        :model-id="modelId"
        :models="modelsForTool"
        :errors="errors"
        :loading="loading"
        :template="selectedTemplate"
        :templates="toolTemplates"
        @submit="submit"
        @reset="resetForm"
        @update:model-id="modelId = $event"
        @use-example="useExample"
        @remove-template="removeTemplate"
        @apply-template="applyTemplateById"
      />

      <div ref="resultWrap" class="result-column">
        <ResultPanel
          :loading="loading"
          :result="result"
          :error="error"
          :request-id="requestId"
          :remaining="remaining"
          :latency="latency"
          :model-label="modelLabel"
          :tool-title="tool.title"
          :saved-id="savedId"
          :image-alt="form.prompt || ''"
          @retry="retry"
          @regenerate="regenerate"
        />
      </div>
    </div>
  </div>
</template>
