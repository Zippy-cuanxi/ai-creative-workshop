<script setup>
import { computed } from 'vue'

import FormField from './FormField.vue'

const props = defineProps({
  tool: { type: Object, required: true },
  values: { type: Object, required: true },
  modelId: { type: String, default: '' },
  models: { type: Array, default: () => [] },
  errors: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  template: { type: Object, default: null },
  templates: { type: Array, default: () => [] }
})

const emit = defineEmits(['submit', 'reset', 'update:modelId', 'use-example', 'remove-template', 'apply-template'])

const selectedModel = computed(() => props.models.find((model) => model.id === props.modelId))
const modelHint = computed(() =>
  selectedModel.value && selectedModel.value.mock
    ? '示例模式：结果在本地生成，不调用第三方 API，也不产生费用。'
    : '模型白名单由后端控制，第三方 API Key 不会暴露给浏览器。'
)

function onModelChange(event) {
  emit('update:modelId', event.target.value)
}

function onTemplateChange(event) {
  emit('apply-template', event.target.value)
}
</script>

<template>
  <form class="card panel" novalidate :aria-busy="loading" @submit.prevent="emit('submit')">
    <div class="panel-head">
      <h2 class="panel-title"><span class="panel-title__dot" aria-hidden="true"></span>填写需求</h2>
      <button type="button" class="btn-quiet" @click="emit('reset')">重置表单</button>
    </div>

    <div v-if="template" class="template-loaded">
      <span>已载入模板「{{ template.title }}」，相关字段已自动填充。</span>
      <button type="button" class="btn-quiet" @click="emit('remove-template')">移除</button>
    </div>

    <div class="form-block form-block--plain">
      <div class="model-row">
        <label class="form-block__label" for="tool-template">Prompt 模板</label>
        <select id="tool-template" class="select" :value="template ? template.id : ''" @change="onTemplateChange">
          <option value="">不使用模板，手动填写</option>
          <option v-for="item in templates" :key="item.id" :value="item.id">{{ item.title }}</option>
        </select>
        <p class="hint">选择模板会自动填充字段，仍可继续修改。</p>
      </div>
    </div>

    <div class="example-row" role="group" aria-label="快速填充示例">
      <span class="hint" style="align-self: center">快速示例</span>
      <button
        v-for="example in tool.examples"
        :key="example.label"
        type="button"
        class="example-btn"
        @click="emit('use-example', example.values)"
      >
        {{ example.label }}
      </button>
    </div>

    <div class="form-grid" style="margin-top: 16px">
      <FormField
        v-for="field in tool.fields"
        :key="field.key"
        :field="field"
        :model-value="values[field.key]"
        :error="errors[field.key] || ''"
        @update:model-value="values[field.key] = $event"
      />
    </div>

    <div class="form-block">
      <div class="model-row">
        <label class="form-block__label" for="tool-model">生成模型</label>
        <select id="tool-model" class="select" :value="modelId" @change="onModelChange">
          <option v-for="model in models" :key="model.id" :value="model.id">
            {{ model.name }}
          </option>
        </select>
        <p class="hint">{{ modelHint }}</p>
      </div>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary" :disabled="loading">
        <span v-if="loading" class="spinner" aria-hidden="true"></span>
        {{ loading ? '正在生成…' : `开始${tool.nav}` }}
      </button>
      <span class="hint">提交即表示同意遵守内容规范；请勿输入隐私或违法内容。</span>
    </div>
  </form>
</template>
