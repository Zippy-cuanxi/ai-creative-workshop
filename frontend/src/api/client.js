const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/+$/, '')
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

let demoModulePromise = null
function loadDemo() {
  if (!demoModulePromise) demoModulePromise = import('../demo/client')
  return demoModulePromise
}

export class ApiError extends Error {
  constructor(message, code = 'INTERNAL_ERROR', extra = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = extra.status || 0
    this.requestId = extra.requestId || ''
    this.retryAfter = extra.retryAfter || 0
    this.field = extra.field || ''
  }
}

async function request(path, options = {}) {
  const { method = 'GET', body, timeout = 120000 } = options
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeout)
  try {
    const response = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
      credentials: 'omit'
    })
    let data = null
    try {
      data = await response.json()
    } catch {
      data = null
    }
    if (!response.ok || !data || data.ok === false) {
      const error = (data && data.error) || {}
      throw new ApiError(
        error.message || `请求失败（HTTP ${response.status}）`,
        error.code || 'INTERNAL_ERROR',
        {
          status: response.status,
          requestId: (data && data.request_id) || response.headers.get('X-Request-ID') || '',
          retryAfter: error.retry_after || 0,
          field: error.field || ''
        }
      )
    }
    return data
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (error.name === 'AbortError') {
      throw new ApiError('请求超时，模型可能正在排队，请稍后重试', 'CLIENT_TIMEOUT')
    }
    throw new ApiError('网络连接失败，请检查网络后重试', 'NETWORK_ERROR')
  } finally {
    window.clearTimeout(timer)
  }
}

export const api = {
  async getModels() {
    if (DEMO_MODE) return (await loadDemo()).getModels()
    return request('/models')
  },
  async getTemplates() {
    if (DEMO_MODE) return (await loadDemo()).getTemplates()
    return request('/templates')
  },
  async getUsage(anonymousId) {
    if (DEMO_MODE) return (await loadDemo()).getUsage(anonymousId)
    return request(`/usage?anonymous_id=${encodeURIComponent(anonymousId)}`)
  },
  async getHealth() {
    if (DEMO_MODE) return (await loadDemo()).getHealth()
    return request('/health')
  },
  async generate(payload) {
    if (DEMO_MODE) return (await loadDemo()).generate(payload)
    return request('/generate', { method: 'POST', body: payload, timeout: 150000 })
  }
}
