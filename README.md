# AI 创意工坊

公开可访问的 AI 生成工具站：起名、文案生成、内容改写、图片生成入口，配套 Prompt 模板库与本地历史记录。
免注册、免登录，匿名即可使用；后端只做密钥保护、转发、限流与调用记录。

- 前端：Vue 3 + Vite + Vue Router + Pinia
- 后端：Django + Django REST Framework
- 部署：Docker / Docker Compose + Nginx（也可单容器部署），另有 GitHub Pages 静态演示版

在线体验：<https://zippy-cuanxi.github.io/ai-creative-workshop/>

> 默认**演示模式**：不配置任何第三方密钥也能完整体验四个工具——文本由本地规则模板生成，图片为本地 SVG 占位图，不产生第三方费用。

## 目录结构

```
.
├── backend/
│   ├── config/               # Django 配置、路由、WSGI
│   ├── core/
│   │   ├── views.py          # /api 视图（校验、限流、转发、记录）
│   │   ├── urls.py
│   │   ├── providers.py      # 模型白名单 + OpenAI 兼容接口转发
│   │   ├── service.py        # 生成编排、模板解析
│   │   ├── tooling.py        # 字段校验与 Prompt 组装
│   │   ├── mock_engine.py    # 演示模式（文本 + SVG 占位图）
│   │   ├── ratelimit.py      # 每 IP 每分钟 / 每匿名 ID 每日
│   │   ├── errors.py         # 统一错误结构与异常处理
│   │   ├── models.py         # 调用元数据记录
│   │   ├── templates.json    # 模板库（后端接口数据源）
│   │   └── migrations/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── views/            # 首页、四个工具页、模板库、历史、关于、API 文档、404
│   │   ├── components/       # Header/Footer/表单/结果/模板卡片等
│   │   ├── stores/           # Pinia：应用状态、历史、收藏、模板
│   │   ├── api/client.js     # 统一请求封装与错误映射
│   │   ├── data/tools.js     # 工具字段 schema 与前端校验
│   │   ├── data/templates.json  # 模板库前端兜底（与后端保持一致）
│   │   └── styles/main.css
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── Dockerfile                # 单容器部署（前端构建产物内置到 Django）
├── docker-compose.yml        # frontend/nginx + backend
└── README.md
```

## 本地开发

### 1. 后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate  |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

- 健康检查：<http://127.0.0.1:8000/api/health>
- 模型列表：<http://127.0.0.1:8000/api/models>
- 管理后台（查看调用记录）：<http://127.0.0.1:8000/admin/>，先执行
  `python manage.py createsuperuser`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 <http://127.0.0.1:5173>，Vite 已把 `/api` 代理到 `127.0.0.1:8000`。

### 3. 生产构建预览

```bash
cd frontend && npm run build
# 产物在 frontend/dist
```

### 4. 单端口预览（模拟线上形态）

```bash
cd frontend && npm run build
# Windows:
#   Copy-Item dist\* ..\backend\frontend_dist -Recurse -Force
# macOS / Linux:
#   mkdir -p ../backend/frontend_dist && cp -r dist/* ../backend/frontend_dist/
cd ../backend && python manage.py runserver
```

打开 <http://127.0.0.1:8000>，此时前端与 API 同源，Django 直接托管构建产物。

> WhiteNoise 在启动时扫描静态文件，重新构建前端后需要重启后端进程，否则会拿到旧的资源列表。

在 Windows 上对外提供服务时，建议用 Waitress 代替开发服务器：

```bash
cd backend
set DJANGO_DEBUG=False
set DJANGO_ALLOWED_HOSTS=*
waitress-serve --listen=0.0.0.0:8000 --threads=8 config.wsgi:application
```

同一网络的电脑访问 `http://<本机局域网 IP>:8000`，需要在 Windows 防火墙放行该端口。
临时让外网电脑访问可以用 Cloudflare Quick Tunnel（地址随进程变化，仅用于演示）：

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

## 接入真实模型

后端通过环境变量读取密钥并转发，前端永远不接触密钥。复制 `backend/.env.example` 为 `backend/.env`，按需填写：

```bash
cp backend/.env.example backend/.env
```

`AI_MODELS_JSON` 为模型白名单（JSON 单行）。每一项含义：

| 字段 | 说明 |
| --- | --- |
| `id` | 前端使用的模型 ID |
| `name` | 下拉框显示名称 |
| `provider` | `openai`（OpenAI 兼容）或 `mock` |
| `type` | `text` 或 `image` |
| `upstream_model` | 第三方真实模型名 |
| `base_url` | OpenAI 兼容接口根地址（不含 `/chat/completions`） |
| `api_key_env` | 保存密钥的环境变量名 |
| `max_tokens` | 文本模型最大输出 token（可选） |

示例（文本 + 图像）：

```env
AI_MODELS_JSON=[{"id":"deepseek-chat","name":"DeepSeek Chat","provider":"openai","type":"text","upstream_model":"deepseek-chat","base_url":"https://api.deepseek.com/v1","api_key_env":"DEEPSEEK_API_KEY"},{"id":"gpt-image-1","name":"GPT Image","provider":"openai","type":"image","upstream_model":"gpt-image-1","base_url":"https://api.openai.com/v1","api_key_env":"OPENAI_API_KEY"}]
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-yyy
```

规则：
- 仅当 `base_url` 与对应密钥都存在时，该模型才会出现在 `/api/models`；
- 某类型（文本 / 图片）没有任何可用真实模型时，自动补上演示模型；
- 密钥缺失、额度受限、超时都会映射为可读错误码，不会把上游细节返回给前端。

## 生产部署

> 部署平台必须能运行 Python/Docker。GitHub Pages、纯静态 CDN 等仅托管静态文件的平台
> 无法运行 `/api`，只能看到前端界面而无法生成内容。

### 方式 A：Docker Compose（Nginx + Django，符合前后端分离）

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env：DJANGO_SECRET_KEY、CORS、模型密钥等
docker compose up -d --build
# 访问 http://服务器IP:8080
```

- 前端由 Nginx 托管，`/api` 反向代理到 `backend:8000`；
- 后端由 Gunicorn 启动，启动时自动迁移与收集静态文件；
- SQLite 数据落在 `backend_data` 卷；调用记录可在 `/admin/` 查看。

生产建议：
- 前置 HTTPS（云厂商负载均衡或 Nginx 443 + 证书）；
  `DJANGO_DEBUG=False`、`CORS_ALLOW_ALL=False`，`CORS_ALLOWED_ORIGINS` 填站点域名；
- 同源部署时无需配置 CORS；
- 多实例/多 worker 时，把 `settings.CACHES` 换成 Redis（`django.core.cache.backends.redis.RedisCache`，需安装 `redis` 包），否则限流额度会按 worker 数放大。

### 方式 B：单容器（一个端口托管前后端）

适合只允许暴露一个端口的平台。根目录 `Dockerfile` 会先构建前端，再把 `dist` 放进 Django，由 WhiteNoise + SPA 兜底视图托管：

```bash
docker build -t ai-creative-workshop .
docker run -p 8000:8000 --env-file backend/.env ai-creative-workshop
# 访问 http://localhost:8000
```

平台部署时把监听端口设置为 `8000`，并配置环境变量即可。

### 环境变量速查

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | 开发用固定值 | 生产必须改成随机长字符串（IP 哈希也依赖它） |
| `DJANGO_DEBUG` | `True` | 生产设为 `False` |
| `DJANGO_ALLOWED_HOSTS` | `*` | 生产建议填具体域名 |
| `DJANGO_SQLITE_PATH` | `backend/data/db.sqlite3` | SQLite 路径 |
| `CORS_ALLOW_ALL` | 跟 DEBUG 一致 | 生产设 `False` |
| `CORS_ALLOWED_ORIGINS` | 本地 5173 | CORS 白名单 |
| `RATE_LIMIT_PER_MINUTE` | `10` | 每 IP 每分钟次数 |
| `RATE_LIMIT_PER_DAY` | `100` | 每匿名 ID 每日次数 |
| `UPSTREAM_TIMEOUT_SECONDS` | `45` | 文本模型超时 |
| `UPSTREAM_IMAGE_TIMEOUT_SECONDS` | `90` | 图像模型超时 |
| `UPSTREAM_MAX_RETRIES` | `1` | 超时/5xx 重试次数 |
| `LOG_GENERATION` | `True` | 是否记录调用元数据 |
| `CONTENT_BLOCKLIST` | 少量敏感词 | 逗号分隔，命中返回 `CONTENT_BLOCKED` |
| `AI_MODELS_JSON` | 空 | 模型白名单，见上文 |
| `FRONTEND_DIST` | `backend/frontend_dist` | 单容器模式的前端产物目录 |

## GitHub Pages 静态演示站

- 在线访问：<https://zippy-cuanxi.github.io/ai-creative-workshop/>
- 开源仓库：<https://github.com/Zippy-cuanxi/ai-creative-workshop>

静态版把生成逻辑搬到浏览器：`frontend/src/demo/` 提供起名、文案、改写与 SVG 图片生成，
模板、历史、收藏全部存本地，不请求 `/api`，因此 GitHub Pages 可以直接托管。
仓库中的 Django 转发层、限流与真实模型接入保持不变，按「生产部署」运行即可切换为在线生成。

### 仓库结构

| 位置 | 用途 |
| --- | --- |
| `main` 分支 | 完整源码：Vue3 前端、Django 后端、Docker/Nginx 配置 |
| `gh-pages` 分支 | 构建产物，GitHub Pages 的发布源（`/` 根目录） |
| `.github/workflows/pages.yml` | 推送 `main` 时自动构建并更新 `gh-pages` |
| `frontend/.env.pages` | Pages 构建变量：演示模式、base 路径、hash 路由 |

### 构建与发布

```bash
cd frontend
npm run build:pages
# 产物：frontend/dist，包含 index.html、404.html、.nojekyll、assets/、favicon.svg
```

发布目录就是仓库根目录，因此 base 路径必须是仓库名：

```env
VITE_BASE_PATH=/ai-creative-workshop/
```

如果改了仓库名，同步修改 `frontend/.env.pages`，否则 JS/CSS 会 404。
静态版使用 hash 路由，分享链接形如
`https://zippy-cuanxi.github.io/ai-creative-workshop/#/tools/name`，不依赖服务器重写规则。

### 启用 Pages

1. 打开仓库 Settings → Pages；
2. Source 选择 **Deploy from a branch**；
3. Branch 选择 `gh-pages`，目录选择 `/ (root)`，保存；
4. 等待页面顶部出现 “Your site is live at …”，访问
   `https://<用户名>.github.io/<仓库名>/`。

首次部署也可手动把 `frontend/dist` 的内容提交到 `gh-pages` 分支；后续推送 `main` 时工作流会自动重建。

## API 契约

Base URL：`/api`，全部返回 JSON，无需登录。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/models` | `{models:[{id,name,provider,type,mock}], limits:{perMinute,perDay}, demoMode}` |
| GET | `/api/templates` | 模板列表（前端另有内置 JSON 兜底） |
| POST | `/api/generate` | 生成入口 |
| GET | `/api/usage?anonymous_id=` | 剩余额度 |
| GET | `/api/health` | 健康检查 |

`POST /api/generate` 请求：

```json
{
  "tool": "name",
  "model": "mock-text",
  "anonymous_id": "anon_7f3c9a1b5e8d2c4f",
  "template_id": "name-brand-five",
  "input": { "industry": "校园咖啡品牌", "style": "国潮", "count": 6 }
}
```

成功响应：

```json
{
  "ok": true,
  "request_id": "8c1e5f0a9b2d4c6e",
  "result": { "type": "text", "text": "……", "images": [], "mock": true },
  "usage": {},
  "remaining": { "perMinute": 10, "perDay": 100, "minuteRemaining": 9, "dayRemaining": 99 },
  "model": { "id": "mock-text", "name": "工坊示例模型（演示）", "type": "text", "mock": true }
}
```

失败响应：

```json
{ "ok": false, "request_id": "…", "error": { "code": "RATE_LIMITED", "message": "…", "retry_after": 37 } }
```

错误码：`INVALID_INPUT`、`RATE_LIMITED`、`MODEL_NOT_ALLOWED`、`UPSTREAM_TIMEOUT`、
`UPSTREAM_QUOTA`、`CONTENT_BLOCKED`、`UPSTREAM_ERROR`、`INTERNAL_ERROR`（后两个为扩展码）。

## 风险与边界

1. **第三方费用与额度**：调用真实模型会产生费用，额度耗尽、限流、延迟、价格调整都会直接影响站点。建议设置账户预算上限、额度告警与错误监控（重点看 `UPSTREAM_QUOTA`、`UPSTREAM_TIMEOUT`）。
2. **后端偏薄**：Django 只做转发与治理，不含账号、计费、审计与内容人工复核。需要这些能力时请自行扩展。
3. **国内网络环境**：若上游模型服务在境外，访问可能不稳定；请选择可达的接口地址，或部署在合适的网络区域。
4. **演示模式**：未配置密钥时生成内容为规则模板与 SVG 占位图，仅用于体验流程，不代表真实模型效果。
5. **内容安全**：基础敏感词 + 上游审核，但不能保证 100% 识别；对外发布前必须人工复核。
6. **隐私**：不采集身份信息；后端记录匿名 ID、IP 哈希、工具、模型、状态、耗时、错误码、request_id，不保存 prompt 与正文；历史记录只存浏览器。

## 验收清单

- [x] 无登录可访问：首次访问生成匿名 ID，直接进入工作台
- [x] 四个工具可用：起名 / 文案 / 改写 / 图片，演示模式即可跑通
- [x] 模板可填充：模板库筛选、搜索、收藏、复制、跳转并自动填充
- [x] 历史可管理：自动保存最近 50 条，支持筛选、搜索、复制、重新使用、删除、清空
- [x] 限流生效：完整版为每分钟 / 每日服务端限流，超限返回 429 与 `retry_after`；静态版为浏览器本地同额度计数
- [x] 错误可读：统一错误码 + 中文提示 + request_id + 重试按钮
- [x] 移动端可用：360px 起布局正常，导航折叠，表单与结果上下堆叠
- [x] 风险说明完整：首页风险条、关于页八大章节、API 错误码说明
- [x] 部署文档完整：本地开发、Compose、单容器、环境变量、限流与风险
- [x] GitHub Pages 已上线：`gh-pages` 发布分支、Actions 自动构建、base 路径与 hash 深链验证通过

## 说明

前端 `src/data/templates.json` 与后端 `core/templates.json` 为同一份模板数据：
后端接口是线上数据源，前端文件用于接口不可用时的兜底展示。修改模板时请同步两处。

GitHub Pages 构建通过 `VITE_DEMO_MODE=true` 启用浏览器本地生成（`frontend/src/demo/`），
不请求 `/api`；完整 Django 版本按「生产部署」运行后仍使用服务端转发与限流。
