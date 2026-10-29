export function createId(prefix = '') {
  const bytes = new Uint8Array(16)
  if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
    window.crypto.getRandomValues(bytes)
  } else {
    for (let index = 0; index < bytes.length; index += 1) {
      bytes[index] = Math.floor(Math.random() * 256)
    }
  }
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('')
  return prefix + hex
}

export function shortId(value = '', keep = 6) {
  if (!value) return ''
  return value.length <= keep ? value : `${value.slice(0, keep)}…`
}
