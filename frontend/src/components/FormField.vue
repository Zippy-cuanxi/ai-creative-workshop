<script setup>
import { computed } from 'vue'

const props = defineProps({
  field: { type: Object, required: true },
  modelValue: { type: [String, Number], default: '' },
  error: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const inputId = computed(() => `field-${props.field.key}`)
const hintId = computed(() => `${inputId.value}-hint`)
const errorId = computed(() => `${inputId.value}-error`)
const options = computed(() =>
  (props.field.options || []).map((option) =>
    typeof option === 'string' ? { value: option, label: option } : option
  )
)
const describedBy = computed(() => {
  const ids = []
  if (props.field.hint) ids.push(hintId.value)
  if (props.error) ids.push(errorId.value)
  return ids.length ? ids.join(' ') : undefined
})
const length = computed(() => String(props.modelValue ?? '').length)

function onInput(event) {
  emit('update:modelValue', event.target.value)
}
</script>

<template>
  <div class="field" :class="{ 'field--wide': field.span === 2 }">
    <label class="field__label" :for="inputId">
      {{ field.label }}
      <span v-if="field.required" class="field__required" aria-hidden="true">*</span>
    </label>

    <select
      v-if="field.type === 'select'"
      :id="inputId"
      class="select"
      :value="modelValue"
      :aria-describedby="describedBy"
      :aria-invalid="error ? 'true' : undefined"
      :aria-required="field.required ? 'true' : undefined"
      @change="onInput"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>

    <textarea
      v-else-if="field.type === 'textarea'"
      :id="inputId"
      class="textarea"
      :rows="field.rows || 3"
      :placeholder="field.placeholder"
      :maxlength="field.maxlength"
      :value="modelValue"
      :aria-describedby="describedBy"
      :aria-invalid="error ? 'true' : undefined"
      :aria-required="field.required ? 'true' : undefined"
      :required="field.required"
      @input="onInput"
    />

    <input
      v-else
      :id="inputId"
      class="input"
      :type="field.type === 'number' ? 'number' : 'text'"
      :inputmode="field.type === 'number' ? 'numeric' : undefined"
      :min="field.min"
      :max="field.max"
      :placeholder="field.placeholder"
      :maxlength="field.maxlength"
      :value="modelValue"
      :aria-describedby="describedBy"
      :aria-invalid="error ? 'true' : undefined"
      :aria-required="field.required ? 'true' : undefined"
      :required="field.required"
      @input="onInput"
    />

    <div class="field__hint-row">
      <span :id="hintId" class="hint">{{ field.hint || '' }}</span>
      <span v-if="field.maxlength" class="field__count">{{ length }}/{{ field.maxlength }}</span>
    </div>

    <p v-if="error" :id="errorId" class="field__error" role="alert">
      <span aria-hidden="true">!</span>{{ error }}
    </p>
  </div>
</template>
