<script setup>
import { computed } from 'vue'

import { useAppStore } from '../stores/app'
import { shortId } from '../utils/id'

const appStore = useAppStore()
const staticDemo = import.meta.env.VITE_DEMO_MODE === 'true'

const anonDisplay = computed(() =>
  appStore.anonymousId ? shortId(appStore.anonymousId, 8) : '生成中…'
)
</script>

<template>
  <div class="container">
    <section class="page-head">
      <span class="eyebrow">About · Risk</span>
      <h1 class="page-head__title">关于与风险说明</h1>
      <p class="page-head__lead">
        AI 创意工坊是一个公开体验站点：不需要登录，直接用。为了让所有人用得久一点，
        我们对调用做了限流与记录，也把依赖第三方服务带来的不确定性写在这里。
      </p>
      <div class="page-head__meta">
        <span class="chip chip--dot">公开访问</span>
        <span class="chip">匿名 ID：{{ anonDisplay }}</span>
        <span class="chip">每分钟 {{ appStore.limits.perMinute }} 次</span>
        <span class="chip">每日 {{ appStore.limits.perDay }} 次</span>
      </div>
    </section>

    <div v-if="staticDemo" class="callout" style="margin-bottom: 18px">
      当前是 <strong>GitHub Pages 静态演示版</strong>：起名、文案、改写与图片全部在浏览器本地生成，
      不调用第三方 API，也不产生费用。仓库中的 Django 转发层、限流与真实模型接入代码保持不变，
      按 README 部署到 Python 主机即可切换为在线生成。
    </div>
    <div v-else-if="appStore.demoMode" class="callout" style="margin-bottom: 18px">
      当前站点运行在<strong>演示模式</strong>：起名、文案、改写由本地规则模板生成，图片为本地 SVG
      占位图，不调用第三方 API，也不产生费用。管理员配置模型白名单与密钥后，页面会自动切换为真实模型。
    </div>

    <article class="card card-pad prose">
      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">01</span>这是什么</h2>
        <p>
          一个面向协会成员、体验 AI 的同学与公开访客的轻量工具站，包含四个工具：
          起名、文案生成、内容改写、图片生成入口，配套 Prompt 模板库与本地历史记录。
        </p>
        <ul>
          <li>免注册、免登录，首次访问即生成匿名身份。</li>
          <li>前端只负责界面、校验与本地数据；后端只做转发与治理，不存正文。</li>
          <li>所有生成结果都应在使用前人工复核，尤其是事实、数字与对外发布内容。</li>
        </ul>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">02</span>怎么用</h2>
        <ul>
          <li>选择工具，或从模板库点「使用此模板」自动带入字段。</li>
          <li>填写需求，点击生成；失败会显示错误码、request_id 与重试入口。</li>
          <li>成功后复制结果，或到历史记录里重新使用同一组输入。</li>
          <li>历史记录默认只保存在当前浏览器，最多 50 条，可单条删除或一键清空。</li>
        </ul>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">03</span>匿名身份与限流</h2>
        <dl class="definition-list">
          <div class="definition">
            <dt>匿名 ID</dt>
            <dd>首次访问时在本地生成并存入 localStorage，仅用于额度统计与防滥用，不关联手机号、邮箱或账号。</dd>
          </div>
          <div class="definition">
            <dt>网络哈希</dt>
            <dd>服务端对客户端 IP 做单向哈希后记录，不保存明文 IP；哈希值无法还原为原始地址。</dd>
          </div>
          <div class="definition">
            <dt>限流规则</dt>
            <dd>每个网络每分钟 {{ appStore.limits.perMinute }} 次、每个匿名 ID 每天 {{ appStore.limits.perDay }} 次，均可由部署者调整。</dd>
          </div>
          <div class="definition">
            <dt>超限表现</dt>
            <dd>返回 HTTP 429 与错误码 RATE_LIMITED，并在页面提示恢复所需时间；额度会随时间窗口自动恢复。</dd>
          </div>
          <div class="definition">
            <dt>额度查询</dt>
            <dd>页面顶部显示今日剩余次数；也可通过 <code class="code-inline">GET /api/usage</code> 查询。</dd>
          </div>
        </dl>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">04</span>第三方模型风险</h2>
        <ul>
          <li>费用：每次调用可能产生第三方费用，由部署者承担；站点本身不向访客收费。</li>
          <li>额度：第三方账户额度耗尽或触发频率限制时，生成会失败并返回 UPSTREAM_QUOTA。</li>
          <li>延迟：模型排队或网络波动会导致响应变慢，超过超时时间会返回 UPSTREAM_TIMEOUT。</li>
          <li>价格与规则：第三方可能调整价格、模型名称或内容政策，本站行为随之变化。</li>
          <li>内容审核：上游安全审核可能拒绝请求，页面会提示 CONTENT_BLOCKED。</li>
        </ul>
        <div class="callout">
          建议部署者配置额度告警与错误监控：关注 UPSTREAM_QUOTA、UPSTREAM_TIMEOUT 的出现频率，
          并为第三方账户设置预算上限，避免意外消耗。
        </div>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">05</span>后端为什么这么薄</h2>
        <p>
          Django 层只承担五件事：隐藏密钥、参数校验、限流、转发、记录调用元数据。
          没有账号体系、计费和复杂业务编排，因此：
        </p>
        <ul>
          <li>无法按用户计费或区分会员权益，额度是站点级统一规则。</li>
          <li>不保存完整 prompt 与正文，历史记录由浏览器本地负责。</li>
          <li>多进程部署时，本地内存限流会按 worker 数放大，生产建议换成 Redis 计数。</li>
          <li>若需要审计、团队协作或长期留存，应在后端接入数据库与权限系统后再扩展。</li>
        </ul>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">06</span>隐私与日志</h2>
        <ul>
          <li>不要求登录，不采集手机号、邮箱、身份证等个人身份信息。</li>
          <li>第三方 API Key 只存在于服务端环境变量，前端代码与浏览器均无法获取。</li>
          <li>调用日志只记录匿名 ID、IP 哈希、工具、模型、状态、耗时、错误码与 request_id。</li>
          <li>日志写入失败不会影响生成主流程；敏感信息不会被写入日志。</li>
          <li>使用浏览器「清除站点数据」即可同时清除匿名 ID、历史记录与模板收藏。</li>
        </ul>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">07</span>内容安全与免责</h2>
        <ul>
          <li>服务端做基础敏感词拦截，上游模型另有安全审核，但不能保证 100% 识别。</li>
          <li>禁止生成违法、暴力、色情、歧视、侵犯他人权益或危害公共安全的内容。</li>
          <li>生成结果由第三方模型产生，不构成专业建议；对外发布前请自行核实。</li>
          <li>站点可按运营需要调整限流、下线工具或切换模型，恕不另行通知。</li>
        </ul>
      </section>

      <section class="prose-section">
        <h2 class="prose-section__title"><span class="prose-section__index">08</span>后续可扩展</h2>
        <ul>
          <li>多模型切换：当前已支持模型白名单与前端下拉，可继续接入更多供应商。</li>
          <li>Prompt 模板市场：预留模板接口与「即将上线」入口，未来可支持作者上传与收藏排行。</li>
          <li>浏览器插件版：可通过同一套 <RouterLink to="/docs/api">API</RouterLink> 提供划词改写与右键生成。</li>
          <li>团队空间：在账号体系成熟后，增加共享历史、配额分配与审计。</li>
        </ul>
      </section>
    </article>
  </div>
</template>
