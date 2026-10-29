import { defineStore } from 'pinia'

import { api } from '../api/client'
import bundled from '../data/templates.json'

let loadPromise = null

export const useTemplatesStore = defineStore('templates', {
  state: () => ({
    items: [],
    categories: [],
    version: 0,
    source: 'bundled',
    loading: false,
    loaded: false
  }),
  getters: {
    byId: (state) => (id) => state.items.find((item) => item.id === id) || null,
    hot: (state) => state.items.filter((item) => item.hot),
    forTool: (state) => (tool) => state.items.filter((item) => item.tool === tool)
  },
  actions: {
    async load(force = false) {
      if (this.loaded && !force) return
      if (loadPromise) return loadPromise
      loadPromise = (async () => {
        this.loading = true
        try {
          const data = await api.getTemplates()
          this.items = data.templates || []
          this.categories = data.categories || []
          this.version = data.version || 1
          this.source = 'api'
        } catch {
          this.items = bundled.templates || []
          this.categories = bundled.categories || []
          this.version = bundled.version || 1
          this.source = 'bundled'
        } finally {
          this.loading = false
          this.loaded = true
        }
      })()
      try {
        await loadPromise
      } finally {
        loadPromise = null
      }
    }
  }
})
