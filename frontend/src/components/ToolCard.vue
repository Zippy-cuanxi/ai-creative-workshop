<script setup>
import ToolGlyph from './ToolGlyph.vue'

defineProps({
  tool: { type: Object, required: true },
  index: { type: Number, default: 1 }
})
</script>

<template>
  <RouterLink
    :to="tool.path"
    class="tool-card card"
    :class="`tool-card--${tool.accent}`"
    :aria-label="`${tool.title}：${tool.tagline}`"
  >
    <div class="tool-card__top">
      <span class="tool-glyph">
        <ToolGlyph :name="tool.glyph" :size="22" />
      </span>
      <span class="tool-index">{{ String(index).padStart(2, '0') }}</span>
    </div>
    <h3 class="tool-card__title">{{ tool.title }}</h3>
    <p class="tool-card__tagline">{{ tool.tagline }}</p>
    <p class="tool-card__example">示例：{{ tool.examples[0].label }}</p>
    <span class="tool-card__cta">进入工具</span>
  </RouterLink>
</template>
