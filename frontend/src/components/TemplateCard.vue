<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useToast } from '../composables/useToast'
import { toolByKey } from '../data/tools'
import { useFavoritesStore } from '../stores/favorites'
import { copyText } from '../utils/clipboard'

const props = defineProps({
  template: { type: Object, required: true }
})

const router = useRouter()
const favorites = useFavoritesStore()
const toast = useToast()

const tool = computed(() => toolByKey[props.template.tool])
const isFavorite = computed(() => favorites.has(props.template.id))

function formatVariable(name) {
  return `{{${name}}}`
}

function toggleFavorite() {
  const added = favorites.toggle(props.template.id)
  toast.push(added ? '已收藏该模板' : '已取消收藏')
}

async function copyTemplate() {
  const ok = await copyText(props.template.content)
  if (ok) toast.success('模板内容已复制')
  else toast.error('复制失败，请手动选择文本')
}

function useTemplate() {
  if (!tool.value) return
  router.push({ path: tool.value.path, query: { template: props.template.id } })
}
</script>

<template>
  <article class="card template-card">
    <div class="template-card__head">
      <div>
        <h3 class="template-card__title">{{ template.title }}</h3>
        <p class="template-card__scene">{{ tool ? tool.nav : template.tool }} · {{ template.scene }}</p>
      </div>
      <button
        type="button"
        class="fav-btn"
        :aria-pressed="isFavorite"
        :aria-label="isFavorite ? `取消收藏 ${template.title}` : `收藏 ${template.title}`"
        @click="toggleFavorite"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" :fill="isFavorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 3.6l2.6 5.5 6 .8-4.4 4.2 1.1 5.9L12 17.2 6.7 20l1.1-5.9L3.4 9.9l6-.8z" />
        </svg>
      </button>
    </div>

    <p class="template-card__content">{{ template.content }}</p>

    <div class="template-card__variables" aria-label="模板变量">
      <span v-for="variable in template.variables" :key="variable" class="chip">
        {{ formatVariable(variable) }}
      </span>
    </div>

    <div class="template-card__actions">
      <button type="button" class="btn btn-sm btn-primary" @click="useTemplate">使用此模板</button>
      <button type="button" class="btn btn-sm btn-ghost" @click="copyTemplate">复制内容</button>
    </div>
  </article>
</template>
