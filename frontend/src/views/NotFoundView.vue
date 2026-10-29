<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="container">
    <div class="empty-state" style="margin-top: 30px; padding: 60px 24px">
      <span class="eyebrow">404</span>
      <h1 class="page-head__title" style="margin-top: 6px">这个页面不在工坊里</h1>
      <p class="empty-state__text">
        可能链接写错了，或者该工具已经下线。回到工作台重新选一个工具吧。
      </p>
      <p class="hint mono">当前路径：{{ route.fullPath }}</p>
      <div class="hero-actions" style="margin-top: 6px">
        <RouterLink to="/" class="btn btn-primary">回到工作台</RouterLink>
        <RouterLink to="/templates" class="btn btn-ghost">浏览模板库</RouterLink>
      </div>
    </div>
  </div>
</template>
