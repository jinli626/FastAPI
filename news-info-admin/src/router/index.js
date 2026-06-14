import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth-token'
import Layout from '@/layout/index.vue'

// 业务路由（带 meta.icon/title 的会自动渲染到侧边栏；hidden 的不显示）
export const menuRoutes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据看板', icon: 'DataLine' },
      },
      {
        path: 'news',
        name: 'NewsList',
        component: () => import('@/views/news/list.vue'),
        meta: { title: '新闻管理', icon: 'Document' },
      },
      {
        path: 'news/create',
        name: 'NewsCreate',
        component: () => import('@/views/news/edit.vue'),
        meta: { title: '发布新闻', hidden: true, activeMenu: '/news' },
      },
      {
        path: 'news/edit/:id',
        name: 'NewsEdit',
        component: () => import('@/views/news/edit.vue'),
        meta: { title: '编辑新闻', hidden: true, activeMenu: '/news' },
      },
      {
        path: 'category',
        name: 'Category',
        component: () => import('@/views/category/index.vue'),
        meta: { title: '分类管理', icon: 'Files' },
      },
    ],
  },
]

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' },
  },
  ...menuRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 新闻管理后台` : '新闻管理后台'
  const token = getToken()

  if (to.path === '/login') {
    // 已登录访问登录页则回首页
    token ? next('/') : next()
  } else {
    token ? next() : next('/login')
  }
})

export default router
