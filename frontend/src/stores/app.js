import { defineStore } from 'pinia'

import { api } from '../api/client'
import { createId } from '../utils/id'
import { readText, writeText } from '../utils/storage'

const ANON_KEY = 'acw:anonymous_id'
const MODEL_KEY = 'acw:default_model'
const FALLBACK_LIMITS = { perMinute: 10, perDay: 100 }

const OFFLINE_MODELS = [
  { id: 'mock-text', name: '工坊示例模型（未连接后端）', provider: 'mock', type: 'text', mock: true },
  { id: 'mock-image', name: '工坊示例画师（未连接后端）', provider: 'mock', type: 'image', mock: true }
]

function ensureAnonymousId() {
  const existing = readText(ANON_KEY)
  if (/^[A-Za-z0-9_-]{8,64}$/.test(existing)) return existing
  const created = createId('anon_')
  writeText(ANON_KEY, created)
  return created
}

let initPromise = null

export const useAppStore = defineStore('app', {
  state: () => ({
    anonymousId: '',
    models: [],
    limits: { ...FALLBACK_LIMITS },
    usage: { minuteRemaining: null, dayRemaining: null },
    defaultModel: '',
    demoMode: false,
    loading: false,
    ready: false,
    offline: false,
    error: ''
  }),
  getters: {
    textModels: (state) => state.models.filter((model) => model.type === 'text'),
    imageModels: (state) => state.models.filter((model) => model.type === 'image'),
    modelsFor: (state) => (type) => state.models.filter((model) => model.type === type),
    modelById: (state) => (id) => state.models.find((model) => model.id === id) || null,
    dayRemaining: (state) => state.usage.dayRemaining
  },
  actions: {
    async init() {
      if (initPromise) return initPromise
      initPromise = (async () => {
        this.anonymousId = ensureAnonymousId()
        await this.loadModels()
        await this.refreshUsage()
      })()
      try {
        await initPromise
      } finally {
        initPromise = null
      }
    },
    async loadModels() {
      this.loading = true
      this.error = ''
      try {
        const data = await api.getModels()
        this.models = data.models || []
        this.limits = { ...FALLBACK_LIMITS, ...(data.limits || {}) }
        this.demoMode = Boolean(data.demoMode)
        this.offline = false
        const stored = readText(MODEL_KEY)
        const preferred =
          this.models.find((model) => model.id === stored && model.type === 'text') ||
          this.textModels[0]
        this.defaultModel = preferred ? preferred.id : ''
      } catch (error) {
        this.offline = true
        this.error = error.message || '无法连接后端服务'
        this.models = OFFLINE_MODELS
        this.limits = { ...FALLBACK_LIMITS }
        this.demoMode = true
        this.defaultModel = OFFLINE_MODELS[0].id
      } finally {
        this.loading = false
        this.ready = true
      }
    },
    setDefaultModel(modelId) {
      this.defaultModel = modelId
      writeText(MODEL_KEY, modelId)
    },
    applyRemaining(remaining) {
      if (!remaining) return
      this.usage = {
        minuteRemaining: remaining.minuteRemaining ?? this.usage.minuteRemaining,
        dayRemaining: remaining.dayRemaining ?? this.usage.dayRemaining
      }
    },
    async refreshUsage() {
      if (!this.anonymousId) return
      try {
        const data = await api.getUsage(this.anonymousId)
        if (data.usage) this.usage = { ...this.usage, ...data.usage }
        if (data.limits) this.limits = { ...this.limits, ...data.limits }
      } catch {
        /* 额度查询失败不阻塞使用 */
      }
    }
  }
})
