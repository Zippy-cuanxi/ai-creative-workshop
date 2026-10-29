import bundled from '../data/templates.json'
import { readJSON, writeJSON } from '../utils/storage'
import { createId } from '../utils/id'
import { generateLocal } from './engine'

const QUOTA_KEY = 'acw:demo:quota:v1'
const LIMITS = { perMinute: 10, perDay: 100 }

const MODELS = [
  {
    id: 'mock-text',
    name: '工坊示例模型（本地演示）',
    provider: 'mock',
    type: 'text',
    mock: true
  },
  {
    id: 'mock-image',
    name: '工坊示例画师（本地演示）',
    provider: 'mock',
    type: 'image',
    mock: true
  }
]

class DemoError extends Error {
  constructor(message, code, extra = {}) {
    super(message)
    this.name = 'DemoError'
    this.code = code
    this.status = extra.status || 400
    this.requestId = extra.requestId || ''
    this.retryAfter = extra.retryAfter || 0
    this.field = extra.field || ''
  }
}

function todayKey() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

function secondsToMidnight() {
  const now = new Date()
  const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
  return Math.max(1, Math.round((tomorrow - now) / 1000))
}

function secondsToNextMinute() {
  return Math.max(1, 60 - new Date().getSeconds())
}

function readQuota() {
  const now = Date.now()
  const state = readJSON(QUOTA_KEY, {})
  const minute = Math.floor(now / 60000)
  const day = todayKey()
  return {
    minute,
    minuteCount: state.minute === minute ? Number(state.minuteCount) || 0 : 0,
    day,
    dayCount: state.day === day ? Number(state.dayCount) || 0 : 0
  }
}

function saveQuota(state) {
  writeJSON(QUOTA_KEY, state)
}

function remainingOf(state) {
  return {
    perMinute: LIMITS.perMinute,
    perDay: LIMITS.perDay,
    minuteRemaining: Math.max(0, LIMITS.perMinute - state.minuteCount),
    dayRemaining: Math.max(0, LIMITS.perDay - state.dayCount)
  }
}

export function getModels() {
  return {
    ok: true,
    models: MODELS,
    limits: LIMITS,
    demoMode: true
  }
}

export function getTemplates() {
  return {
    ok: true,
    version: bundled.version || 1,
    categories: bundled.categories || [],
    templates: bundled.templates || []
  }
}

export function getUsage() {
  const state = readQuota()
  return { ok: true, limits: LIMITS, usage: remainingOf(state) }
}

export function getHealth() {
  return {
    ok: true,
    status: 'healthy',
    service: 'ai-creative-workshop-static',
    version: '1.0.0',
    demoMode: true
  }
}

function consumeQuota() {
  const state = readQuota()
  if (state.minuteCount >= LIMITS.perMinute) {
    const retryAfter = secondsToNextMinute()
    throw new DemoError(
      `请求过于频繁，每个浏览器每分钟最多 ${LIMITS.perMinute} 次，请 ${retryAfter} 秒后再试`,
      'RATE_LIMITED',
      { status: 429, retryAfter }
    )
  }
  if (state.dayCount >= LIMITS.perDay) {
    const retryAfter = secondsToMidnight()
    throw new DemoError(
      `今日演示额度已用完，每个浏览器每天最多 ${LIMITS.perDay} 次，请明天再来`,
      'RATE_LIMITED',
      { status: 429, retryAfter }
    )
  }
  state.minuteCount += 1
  state.dayCount += 1
  saveQuota(state)
  return remainingOf(state)
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function generate(payload) {
  const started = performance.now()
  await delay(120 + Math.random() * 260)
  const remaining = consumeQuota()
  const result = generateLocal(payload.tool, payload.input)
  const mail = {
    ok: true,
    request_id: createId('demo_'),
    result: { ...result, mock: true, usage: {} },
    usage: {},
    remaining,
    model: {
      id: payload.model,
      name: MODELS.find((model) => model.id === payload.model)?.name || '本地演示模型',
      type: result.type,
      mock: true
    },
    latency_ms: Math.max(1, Math.round(performance.now() - started))
  }
  return mail
}
