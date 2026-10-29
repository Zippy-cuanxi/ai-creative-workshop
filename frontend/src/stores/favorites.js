import { defineStore } from 'pinia'

import { readJSON, writeJSON } from '../utils/storage'

const KEY = 'acw:favorites:v1'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    ids: [],
    loaded: false
  }),
  getters: {
    has: (state) => (id) => state.ids.includes(id),
    count: (state) => state.ids.length
  },
  actions: {
    load() {
      if (this.loaded) return
      const stored = readJSON(KEY, [])
      this.ids = Array.isArray(stored) ? stored.filter((item) => typeof item === 'string') : []
      this.loaded = true
    },
    toggle(id) {
      this.load()
      this.ids = this.ids.includes(id)
        ? this.ids.filter((item) => item !== id)
        : [...this.ids, id]
      writeJSON(KEY, this.ids)
      return this.ids.includes(id)
    }
  }
})
