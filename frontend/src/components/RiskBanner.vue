<script setup>
const staticDemo = import.meta.env.VITE_DEMO_MODE === 'true'
</script>

<template>
  <div class="risk-strip" role="note">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
      <path d="M12 8v5" />
      <circle cx="12" cy="16.6" r="0.9" fill="currentColor" stroke="none" />
      <path d="M10.3 3.8L2.6 17.2A2 2 0 0 0 4.4 20h15.2a2 2 0 0 0 1.8-2.8L13.7 3.8a2 2 0 0 0-3.4 0z" />
    </svg>
    <span class="risk-strip__label">公开体验</span>
    <p v-if="staticDemo">
      无需登录，匿名即可使用。当前为 GitHub Pages 静态版，生成在浏览器本地完成，不调用第三方模型；
      历史仅保存在本浏览器。
      <RouterLink to="/about">查看技术说明</RouterLink>
    </p>
    <p v-else>
      无需登录，匿名即可使用；按网络与匿名 ID 限流。第三方模型可能延迟、限流或额度不足，
      生成内容请自行核验。
      <RouterLink to="/about">完整风险说明</RouterLink>
    </p>
  </div>
</template>

