<script setup>
const staticDemo = import.meta.env.VITE_DEMO_MODE === 'true'
</script>

<template>
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <span class="footer-brand__name">AI 创意工坊</span>
          <span class="footer-brand__text">
            面向协会成员与所有体验 AI 的同学：免登录、直接用、风险透明。
            本站仅做请求转发与限流，生成结果由第三方模型提供。
          </span>
        </div>
        <nav class="footer-links" aria-label="页脚导航">
          <RouterLink to="/about">关于与风险</RouterLink>
          <RouterLink to="/docs/api">API 文档</RouterLink>
          <RouterLink to="/templates">模板库</RouterLink>
          <span class="muted" title="后续版本提供浏览器划词与右键生成">浏览器插件版 · 敬请期待</span>
        </nav>
      </div>
      <div class="footer-note">
        <span>© 2026 AI 创意工坊 · 公开体验站点</span>
        <span v-if="staticDemo">GitHub Pages 静态演示版 · 生成在浏览器本地完成</span>
        <span v-else>历史记录仅保存在本浏览器；后端只记录匿名调用元数据。</span>
      </div>
    </div>
  </footer>
</template>
