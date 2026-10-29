<script setup>
import { computed, onMounted, ref } from 'vue'

import TemplateCard from '../components/TemplateCard.vue'
import { useFavoritesStore } from '../stores/favorites'
import { useTemplatesStore } from '../stores/templates'

const store = useTemplatesStore()
const favorites = useFavoritesStore()

const search = ref('')
const category = ref('all')
const onlyFavorites = ref(false)

onMounted(() => {
  store.load()
  favorites.load()
})

const fallbackCategories = [
  { id: 'all', name: '全部' },
  { id: 'name', name: '起名' },
  { id: 'copy', name: '文案' },
  { id: 'rewrite', name: '改写' },
  { id: 'image', name: '图片' }
]

const categories = computed(() => (store.categories.length ? store.categories : fallbackCategories))

function countFor(id) {
  if (id === 'all') return store.items.length
  return store.items.filter((item) => item.tool === id).length
}

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  return store.items.filter((item) => {
    if (category.value !== 'all' && item.tool !== category.value) return false
    if (onlyFavorites.value && !favorites.has(item.id)) return false
    if (!keyword) return true
    const haystack = [item.title, item.scene, item.content, ...(item.tags || [])]
      .join(' ')
      .toLowerCase()
    return haystack.includes(keyword)
  })
})

const sourceLabel = computed(() => {
  if (import.meta.env.VITE_DEMO_MODE === 'true') return '内置模板（静态演示版）'
  return store.source === 'api' ? '后端模板接口' : '前端内置 JSON'
})
</script>

<template>
  <div class="container">
    <section class="page-head">
      <span class="eyebrow">Prompt Library</span>
      <h1 class="page-head__title">模板库</h1>
      <p class="page-head__lead">
        把常用的提问方式沉淀成模板。选择分类或搜索关键词，点「使用此模板」会跳转到对应工具并自动填充。
        收藏状态保存在本浏览器。
      </p>
      <div class="page-head__meta">
        <span class="chip chip--dot">共 {{ store.items.length }} 套模板</span>
        <span class="chip">收藏 {{ favorites.count }} 套</span>
        <span class="chip" title="模板市场将在后续版本开放作者上传与分成">模板市场 · 即将上线</span>
      </div>
    </section>

    <div class="filter-bar">
      <div class="filter-bar__group" role="group" aria-label="按工具筛选">
        <button
          v-for="item in categories"
          :key="item.id"
          type="button"
          class="chip"
          :class="{ 'chip--active': category === item.id }"
          :aria-pressed="category === item.id"
          @click="category = item.id"
        >
          {{ item.name }} · {{ countFor(item.id) }}
        </button>
      </div>

      <button
        type="button"
        class="chip"
        :class="{ 'chip--active': onlyFavorites }"
        :aria-pressed="onlyFavorites"
        @click="onlyFavorites = !onlyFavorites"
      >
        只看收藏
      </button>

      <div class="search-wrap">
        <label class="sr-only" for="template-search">搜索模板</label>
        <span class="search-icon" aria-hidden="true">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <circle cx="10.5" cy="10.5" r="6.5" />
            <path d="M15.6 15.6L21 21" />
          </svg>
        </span>
        <input
          id="template-search"
          v-model="search"
          class="input"
          type="search"
          placeholder="搜索标题、场景或关键词"
        />
      </div>
    </div>

    <p class="result-note">
      当前显示 {{ filtered.length }} 套 · 数据来源：{{ sourceLabel }}
    </p>

    <div v-if="filtered.length" class="template-grid">
      <TemplateCard v-for="template in filtered" :key="template.id" :template="template" />
    </div>

    <div v-else class="empty-state">
      <p class="empty-state__title">没有匹配的模板</p>
      <p class="empty-state__text">换个关键词，或取消「只看收藏」再试试。</p>
      <button
        type="button"
        class="btn btn-sm btn-ghost"
        @click="search = ''; category = 'all'; onlyFavorites = false"
      >
        清除筛选
      </button>
    </div>
  </div>
</template>
