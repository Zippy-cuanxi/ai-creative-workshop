import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'

const ToolView = () => import('../views/ToolView.vue')
const TemplatesView = () => import('../views/TemplatesView.vue')
const HistoryView = () => import('../views/HistoryView.vue')
const AboutView = () => import('../views/AboutView.vue')
const ApiDocsView = () => import('../views/ApiDocsView.vue')
const NotFoundView = () => import('../views/NotFoundView.vue')

const routes = [
  { path: '/', name: 'home', component: HomeView, meta: { title: '工作台' } },
  {
    path: '/tools/name',
    name: 'tool-name',
    component: ToolView,
    props: { toolKey: 'name' },
    meta: { title: '起名工具' }
  },
  {
    path: '/tools/copy',
    name: 'tool-copy',
    component: ToolView,
    props: { toolKey: 'copy' },
    meta: { title: '文案生成' }
  },
  {
    path: '/tools/rewrite',
    name: 'tool-rewrite',
    component: ToolView,
    props: { toolKey: 'rewrite' },
    meta: { title: '内容改写' }
  },
  {
    path: '/tools/image',
    name: 'tool-image',
    component: ToolView,
    props: { toolKey: 'image' },
    meta: { title: '图片生成' }
  },
  { path: '/templates', name: 'templates', component: TemplatesView, meta: { title: '模板库' } },
  { path: '/history', name: 'history', component: HistoryView, meta: { title: '历史记录' } },
  { path: '/about', name: 'about', component: AboutView, meta: { title: '关于与风险说明' } },
  { path: '/docs/api', name: 'api-docs', component: ApiDocsView, meta: { title: 'API 与插件扩展' } },
  {
    path: '/tools/:pathMatch(.*)*',
    name: 'tool-missing',
    component: NotFoundView,
    meta: { title: '页面不存在' }
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView, meta: { title: '页面不存在' } }
]

const useHashHistory = import.meta.env.VITE_ROUTER_MODE === 'hash'
const history = useHashHistory
  ? createWebHashHistory(import.meta.env.BASE_URL)
  : createWebHistory(import.meta.env.BASE_URL)

const router = createRouter({
  history,
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, top: 88 }
    return { top: 0 }
  }
})

router.afterEach((to) => {
  const title = to.meta && to.meta.title
  document.title = title ? `${title} · AI 创意工坊` : 'AI 创意工坊'
})

export default router
