<script setup>
import { onMounted } from 'vue'

import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ToastHost from './components/ToastHost.vue'
import { useAppStore } from './stores/app'
import { useTemplatesStore } from './stores/templates'
import { useHistoryStore } from './stores/history'
import { useFavoritesStore } from './stores/favorites'

const appStore = useAppStore()
const templateStore = useTemplatesStore()
const historyStore = useHistoryStore()
const favoritesStore = useFavoritesStore()

onMounted(() => {
  historyStore.load()
  favoritesStore.load()
  appStore.init()
  templateStore.load()
})
</script>

<template>
  <a class="skip-link" href="#main-content">跳到主要内容</a>
  <AppHeader />
  <main id="main-content" class="app-main">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
  </main>
  <AppFooter />
  <ToastHost />
</template>
