import { reactive } from 'vue'

const state = reactive({ items: [] })
let counter = 0

function dismiss(id) {
  const index = state.items.findIndex((item) => item.id === id)
  if (index >= 0) state.items.splice(index, 1)
}

function push(message, type = 'info', timeout = 3200) {
  const id = ++counter
  state.items.push({ id, message: String(message), type })
  if (state.items.length > 3) state.items.shift()
  if (timeout > 0) window.setTimeout(() => dismiss(id), timeout)
  return id
}

export function useToast() {
  return {
    items: state.items,
    push,
    success: (message) => push(message, 'success'),
    error: (message) => push(message, 'error', 5200),
    dismiss
  }
}
