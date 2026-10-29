<script setup>
defineProps({
  name: { type: String, default: 'spark' },
  size: { type: [Number, String], default: 22 }
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <template v-if="name === 'spark'">
      <path d="M12 3.2l2 5.3 5.3 2-5.3 2-2 5.3-2-5.3-5.3-2 5.3-2z" />
      <path d="M18.5 16.5v3.5M16.8 18.2h3.5" />
    </template>
    <template v-else-if="name === 'pen'">
      <path d="M4 20l4.2-1L18 8.2a2.1 2.1 0 0 0-3-3L5.2 15.8 4 20z" />
      <path d="M13.4 6.2l3 3" />
    </template>
    <template v-else-if="name === 'swap'">
      <path d="M4 8h13.5L14 4.5" />
      <path d="M20 16H6.5L10 19.5" />
    </template>
    <template v-else>
      <rect x="3" y="4.5" width="18" height="15" rx="2.2" />
      <circle cx="8.6" cy="9.6" r="1.5" />
      <path d="M4 17l4.8-4 3 2 3.3-3.2L20 17" />
    </template>
  </svg>
</template>
