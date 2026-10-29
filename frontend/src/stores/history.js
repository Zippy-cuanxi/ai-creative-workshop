import { defineStore } from 'pinia'

import { readJSON, writeJSON } from '../utils/storage'

const KEY = 'acw:history:v1'
const MAX_RECORDS = 50
const MAX_IMAGE_CHARS = 200000

function sanitizeImages(images) {
  if (!Array.isArray(images)) return []
  return images
    .filter((item) => typeof item === 'string' && item.length > 0)
    .map((item) => (item.length > MAX_IMAGE_CHARS ? '' : item))
    .filter(Boolean)
}

export const useHistoryStore = defineStore('history', {
  state: () => ({
    records: [],
    loaded: false
  }),
  getters: {
    latest: (state) => (count = 3) => state.records.slice(0, count),
    count: (state) => state.records.length
  },
  actions: {
    load() {
      if (this.loaded) return
      const stored = readJSON(KEY, [])
      this.records = Array.isArray(stored) ? stored : []
      this.loaded = true
    },
    persist() {
      if (!writeJSON(KEY, this.records)) {
        /* 存储空间不足时保留最近 10 条再试一次 */
        this.records = this.records.slice(0, 10)
        writeJSON(KEY, this.records)
      }
    },
    add(record) {
      this.load()
      const entry = {
        id: record.id,
        createdAt: record.createdAt || new Date().toISOString(),
        tool: record.tool,
        toolTitle: record.toolTitle,
        model: record.model,
        modelName: record.modelName,
        requestId: record.requestId || '',
        input: record.input || {},
        inputSummary: record.inputSummary || '',
        resultType: record.resultType || 'text',
        text: String(record.text || '').slice(0, 6000),
        images: sanitizeImages(record.images),
        status: record.status || 'ok',
        mock: Boolean(record.mock),
        templateId: record.templateId || ''
      }
      this.records = [entry, ...this.records.filter((item) => item.id !== entry.id)].slice(0, MAX_RECORDS)
      this.persist()
      return entry
    },
    remove(id) {
      this.records = this.records.filter((item) => item.id !== id)
      this.persist()
    },
    clear() {
      this.records = []
      this.persist()
    }
  }
})
