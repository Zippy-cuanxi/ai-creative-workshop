<script setup>
import { useAppStore } from '../stores/app'

const appStore = useAppStore()
const staticDemo = import.meta.env.VITE_DEMO_MODE === 'true'

const endpoints = [
  { method: 'GET', path: '/api/models', desc: '模型白名单、限流配置与演示模式标记' },
  { method: 'GET', path: '/api/templates', desc: '模板库只读列表（前端另有内置 JSON 兜底）' },
  { method: 'POST', path: '/api/generate', desc: '统一生成入口，按 tool 分发到起名 / 文案 / 改写 / 图片' },
  { method: 'GET', path: '/api/usage', desc: '查询当前匿名 ID 与网络的剩余额度' },
  { method: 'GET', path: '/api/health', desc: '健康检查，用于部署探针与监控' }
]

const errors = [
  { code: 'INVALID_INPUT', desc: '参数缺失、格式不合法或字段超长', action: '按提示修正表单后重试' },
  { code: 'RATE_LIMITED', desc: '触发每分钟或每日限流', action: '等待 retry_after 后重试' },
  { code: 'MODEL_NOT_ALLOWED', desc: '模型不在白名单，或与工具类型不匹配', action: '刷新页面重新选择模型' },
  { code: 'UPSTREAM_TIMEOUT', desc: '第三方模型超时', action: '稍后重试或更换模型' },
  { code: 'UPSTREAM_QUOTA', desc: '第三方额度或频率受限', action: '等待额度恢复，或由管理员充值' },
  { code: 'CONTENT_BLOCKED', desc: '输入或输出未通过安全审核', action: '调整描述，移除敏感内容' },
  { code: 'UPSTREAM_ERROR', desc: '上游服务异常或拒绝请求', action: '重试；持续失败联系管理员' },
  { code: 'INTERNAL_ERROR', desc: '本站未预期错误', action: '凭 request_id 反馈给维护者' }
]

const requestSample = `{
  "tool": "copy",
  "model": "mock-text",
  "anonymous_id": "anon_7f3c9a1b5e8d2c4f",
  "template_id": "copy-xhs",
  "input": {
    "platform": "小红书",
    "topic": "校园读书会招募",
    "audience": "大学生",
    "tone": "亲切",
    "length": "中",
    "selling_points": "每周一次共读、零门槛参与、提供书单",
    "extra": "不要夸张营销词"
  }
}`

const successSample = `{
  "ok": true,
  "request_id": "8c1e5f0a9b2d4c6e",
  "result": {
    "type": "text",
    "text": "标题备选……",
    "images": [],
    "mock": true
  },
  "remaining": { "perMinute": 10, "perDay": 100,
    "minuteRemaining": 9, "dayRemaining": 99 },
  "model": { "id": "mock-text", "name": "工坊示例模型（演示）", "mock": true },
  "latency_ms": 12
}`

const failureSample = `{
  "ok": false,
  "request_id": "d41f8b7c2a0e6953",
  "error": {
    "code": "RATE_LIMITED",
    "message": "请求过于频繁，请 37 秒后再试",
    "retry_after": 37
  }
}`

const curlSample = `curl -X POST {{base}}/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{"tool":"name","model":"mock-text","anonymous_id":"anon_demo_123456","input":{"industry":"校园咖啡品牌","keywords":"手冲,自习","style":"国潮","count":6}}'`

const basePlaceholder = '{{base}}'
</script>

<template>
  <div class="container">
    <section class="page-head">
      <span class="eyebrow">Developers</span>
      <h1 class="page-head__title">API 与插件扩展</h1>
      <p class="page-head__lead">
        前端与浏览器插件都可以调用同一套接口。接口无状态、不需要登录，但必须携带匿名 ID，
        并遵守限流规则。第三方密钥只存在于服务端。
      </p>
      <div class="page-head__meta">
        <span class="chip chip--dot">Base URL：/api</span>
        <span class="chip">JSON over HTTP</span>
        <span class="chip">浏览器插件版 · 敬请期待</span>
      </div>
    </section>

    <div v-if="staticDemo" class="callout callout--teal" style="margin-bottom: 18px">
      静态演示站没有部署 <code class="code-inline">/api</code>：页面内的生成由浏览器本地完成。
      下面的接口契约与示例对应仓库中的 Django 后端，部署到 Python 主机后可原样调用。
    </div>

    <div class="stack-sm">
      <section class="card card-pad">
        <h2 class="section-title" style="font-size: 1.15rem">接口列表</h2>
        <div class="table-scroll" style="margin-top: 12px">
          <table class="api-table">
            <thead>
              <tr>
                <th scope="col">方法</th>
                <th scope="col">路径</th>
                <th scope="col">说明</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="endpoint in endpoints" :key="endpoint.path + endpoint.method">
                <td><code>{{ endpoint.method }}</code></td>
                <td><code>{{ endpoint.path }}</code></td>
                <td>{{ endpoint.desc }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card card-pad">
        <h2 class="section-title" style="font-size: 1.15rem">生成请求示例</h2>
        <p class="hint" style="margin: 8px 0 12px">
          当前站点限流：每分钟 {{ appStore.limits.perMinute }} 次、每日 {{ appStore.limits.perDay }} 次。
          tool 取值为 name / copy / rewrite / image；model 必须来自 /api/models。
        </p>
        <pre class="code-block">{{ requestSample }}</pre>
        <p class="hint" style="margin: 12px 0 6px">成功响应</p>
        <pre class="code-block">{{ successSample }}</pre>
        <p class="hint" style="margin: 12px 0 6px">失败响应</p>
        <pre class="code-block">{{ failureSample }}</pre>
      </section>

      <section class="card card-pad">
        <h2 class="section-title" style="font-size: 1.15rem">错误码</h2>
        <div class="table-scroll" style="margin-top: 12px">
          <table class="api-table">
            <thead>
              <tr>
                <th scope="col">错误码</th>
                <th scope="col">含义</th>
                <th scope="col">建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in errors" :key="item.code">
                <td><code>{{ item.code }}</code></td>
                <td>{{ item.desc }}</td>
                <td>{{ item.action }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card card-pad">
        <h2 class="section-title" style="font-size: 1.15rem">curl 调用</h2>
        <pre class="code-block" style="margin-top: 12px">{{ curlSample }}</pre>
        <p class="hint" style="margin-top: 10px">
          同源部署时把 {{ basePlaceholder }} 换成站点地址即可；跨域调用需要部署者把来源加入 CORS 白名单。
        </p>
      </section>

      <section class="card card-pad">
        <h2 class="section-title" style="font-size: 1.15rem">插件版规划</h2>
        <ul class="prose" style="margin-top: 10px">
          <li>浏览器划词后右键「改写 / 生成文案」，直接复用 /api/generate。</li>
          <li>插件携带独立 anonymous_id，限流与 Web 端互不影响。</li>
          <li>模板市场开放后，插件可订阅模板并同步参数。</li>
          <li>插件版需要额外的来源校验与密钥托管方案，本期只保留接口。</li>
        </ul>
      </section>
    </div>
  </div>
</template>
