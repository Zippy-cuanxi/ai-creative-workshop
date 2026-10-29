<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useToast } from '../composables/useToast'
import { toolByKey, tools } from '../data/tools'
import { useHistoryStore } from '../stores/history'
import { copyText } from '../utils/clipboard'
import { formatDateTime, truncate } from '../utils/format'

const historyStore = useHistoryStore()
const toast = useToast()
const router = useRouter()

const filter = ref('all')
const search = ref('')
const confirmClear = ref(false)

onMounted(() => historyStore.load())

const filtered = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  return historyStore.records.filter((record) => {
    if (filter.value !== 'all' && record.tool !== filter.value) return false
    if (!keyword) return true
    const haystack = [
      record.inputSummary,
      record.text,
      record.modelName,
      record.requestId,
      record.toolTitle
    ]
      .join(' ')
      .toLowerCase()
    return haystack.includes(keyword)
  })
})

function resultPreview(record) {
  if (record.resultType === 'image') {
    return record.images?.length ? `生成 ${record.images.length} 张图片` : '图片结果'
  }
  return truncate(record.text || '', 140)
}

async function copyRecord(record) {
  const value =
    record.resultType === 'image' ? record.images?.[0] || '' : record.text || ''
  if (!value) {
    toast.error('该记录没有可复制的内容')
    return
  }
  const ok = await copyText(value)
  if (ok) toast.success('结果已复制')
  else toast.error('复制失败，请手动选择文本')
}

function reuse(record) {
  try {
    window.sessionStorage.setItem(
      'acw:reuse',
      JSON.stringify({
        toolKey: record.tool,
        values: record.input,
        modelId: record.model
      })
    )
  } catch {
    toast.error('无法写入临时数据，请手动填写')
    return
  }
  router.push(`/tools/${record.tool}`)
}

function removeRecord(record) {
  historyStore.remove(record.id)
  toast.push('已删除该条记录')
}

function clearAll() {
  historyStore.clear()
  confirmClear.value = false
  toast.success('本地历史已清空')
}
</script>

<template>
  <div class="container">
    <section class="page-head">
      <span class="eyebrow">Local History</span>
      <h1 class="page-head__title">历史记录</h1>
      <p class="page-head__lead">
        记录默认仅保存在当前浏览器，最多 50 条。后端只记录匿名 ID、模型、状态、耗时等调用元数据，
        默认不保存完整 prompt 与生成正文。
      </p>
      <div class="page-head__meta">
        <span class="chip chip--dot">本地共 {{ historyStore.records.length }} 条</span>
        <span class="chip">支持筛选、搜索、复制、重新使用</span>
      </div>
    </section>

    <div class="history-toolbar">
      <label class="sr-only" for="history-filter">按工具筛选</label>
      <select id="history-filter" v-model="filter" class="select">
        <option value="all">全部工具</option>
        <option v-for="tool in tools" :key="tool.key" :value="tool.key">{{ tool.title }}</option>
      </select>

      <label class="sr-only" for="history-search">搜索历史</label>
      <input
        id="history-search"
        v-model="search"
        class="input"
        type="search"
        placeholder="搜索输入摘要、结果、request_id"
      />

      <template v-if="!confirmClear">
        <button
          type="button"
          class="btn btn-sm btn-ghost"
          :disabled="!historyStore.records.length"
          @click="confirmClear = true"
        >
          清空全部
        </button>
      </template>
      <template v-else>
        <div class="confirm-row" role="group" aria-label="确认清空历史">
          <span>清空后不可恢复，确认？</span>
          <button type="button" class="btn btn-sm" @click="confirmClear = false">取消</button>
          <button type="button" class="btn btn-sm btn-primary" @click="clearAll">确认清空</button>
        </div>
      </template>
    </div>

    <ul v-if="filtered.length" class="history-list">
      <li v-for="record in filtered" :key="record.id" class="card history-item">
        <img
          v-if="record.resultType === 'image' && record.images?.length"
          class="history-item__thumb"
          :src="record.images[0]"
          alt="历史图片结果缩略图"
        />
        <span v-else class="history-item__thumb history-item__thumb--placeholder" aria-hidden="true">
          {{ toolByKey[record.tool]?.nav?.slice(0, 1) || 'AI' }}
        </span>

        <div>
          <div class="history-item__meta">
            <span>{{ formatDateTime(record.createdAt) }}</span>
            <span>{{ toolByKey[record.tool]?.nav || record.tool }}</span>
            <span>{{ record.modelName || record.model }}</span>
            <span v-if="record.mock">示例模式</span>
          </div>
          <p class="history-item__summary">{{ record.inputSummary || '未填写摘要' }}</p>
          <p class="history-item__result">{{ resultPreview(record) }}</p>
          <p v-if="record.requestId" class="history-item__meta" style="margin-top: 6px">
            <span>request_id：{{ record.requestId }}</span>
          </p>
        </div>

        <div class="history-item__actions">
          <button type="button" class="btn btn-sm btn-ghost" @click="copyRecord(record)">复制结果</button>
          <button type="button" class="btn btn-sm" @click="reuse(record)">重新使用</button>
          <button type="button" class="btn-quiet" @click="removeRecord(record)">删除</button>
        </div>
      </li>
    </ul>

    <div v-else class="empty-state">
      <p class="empty-state__title">{{ historyStore.records.length ? '没有匹配的记录' : '还没有历史记录' }}</p>
      <p class="empty-state__text">
        {{ historyStore.records.length ? '调整筛选条件或清空搜索关键词。' : '生成成功后会自动写入本地历史。' }}
      </p>
      <RouterLink to="/tools/name" class="btn btn-sm btn-primary">去生成一条</RouterLink>
    </div>
  </div>
</template>
