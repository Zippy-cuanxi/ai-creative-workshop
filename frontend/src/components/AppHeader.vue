<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useAppStore } from '../stores/app'
import { shortId } from '../utils/id'

const route = useRoute()
const appStore = useAppStore()
const menuOpen = ref(false)

const navItems = [
  { label: '工作台', to: '/' },
  { label: '起名', to: '/tools/name' },
  { label: '文案', to: '/tools/copy' },
  { label: '改写', to: '/tools/rewrite' },
  { label: '图片', to: '/tools/image' },
  { label: '模板库', to: '/templates' },
  { label: '历史记录', to: '/history' },
  { label: '关于 / 风险', to: '/about' }
]

const quotaTitle = computed(
  () =>
    `限流规则：每个网络每分钟 ${appStore.limits.perMinute} 次，每个匿名访客每天 ${appStore.limits.perDay} 次`
)

const quotaValue = computed(() => {
  const remaining = appStore.usage.dayRemaining
  return remaining === null || remaining === undefined ? '—' : remaining
})

const anonLabel = computed(() =>
  appStore.anonymousId ? `访客 ${shortId(appStore.anonymousId, 6)}` : '访客'
)

function onModelChange(event) {
  appStore.setDefaultModel(event.target.value)
}

function closeMenu() {
  menuOpen.value = false
}

watch(() => route.fullPath, closeMenu)

function onKeydown(event) {
  if (event.key === 'Escape') closeMenu()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <header class="site-header">
    <div class="container header-bar">
      <button
        type="button"
        class="menu-toggle"
        aria-label="导航菜单"
        :aria-expanded="menuOpen"
        aria-controls="mobile-navigation"
        @click="menuOpen = !menuOpen"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
          <template v-if="!menuOpen">
            <path d="M2.5 5h13M2.5 9h13M2.5 13h13" />
          </template>
          <template v-else>
            <path d="M4 4l10 10M14 4L4 14" />
          </template>
        </svg>
      </button>

      <RouterLink to="/" class="brand" @click="closeMenu">
        <span class="brand-mark" aria-hidden="true">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
            <path d="M12 3l2 5.6L20 11l-6 2.4L12 19l-2-5.6L4 11l6-2.4z" />
          </svg>
        </span>
        <span class="brand-text">
          <span class="brand-name">AI 创意工坊</span>
          <span class="brand-sub">Creative Workshop</span>
        </span>
      </RouterLink>

      <nav class="main-nav" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="header-tools">
        <span v-if="appStore.demoMode" class="badge" title="当前使用本地示例模型，不调用第三方 API，也不产生费用">
          演示模式
        </span>
        <span v-else-if="appStore.offline" class="badge">后端未连接</span>

        <label class="sr-only" for="default-model">默认模型</label>
        <select
          v-if="appStore.textModels.length"
          id="default-model"
          class="model-select"
          :value="appStore.defaultModel"
          title="默认模型（适用于起名、文案、改写）"
          @change="onModelChange"
        >
          <option v-for="model in appStore.textModels" :key="model.id" :value="model.id">
            {{ model.name }}
          </option>
        </select>

        <span class="chip quota-chip" :title="quotaTitle">
          今日剩余 <strong>{{ quotaValue }}</strong> 次
        </span>
        <span class="chip anon-chip" title="匿名访客标识，仅用于限流与调用统计">
          {{ anonLabel }}
        </span>
      </div>
    </div>

    <div id="mobile-navigation" class="mobile-nav container" :class="{ 'is-open': menuOpen }">
      <nav aria-label="移动端导航">
        <ul>
          <li v-for="item in navItems" :key="item.to">
            <RouterLink :to="item.to" @click="closeMenu">{{ item.label }}</RouterLink>
          </li>
        </ul>
      </nav>
      <div class="mobile-meta">
        <span class="chip quota-chip" :title="quotaTitle">今日剩余 {{ quotaValue }} 次</span>
        <span class="chip anon-chip">{{ anonLabel }}</span>
        <span v-if="appStore.demoMode" class="badge">演示模式</span>
      </div>
    </div>
  </header>
</template>
