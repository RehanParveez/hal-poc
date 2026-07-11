import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const ROLE_HOME = {
  smallholder: '/farmer/dashboard',
  tenant: '/farmer/dashboard',
  landowner: '/landowner/dashboard',
  bank: '/bank/dashboard',
  factory: '/factory/dashboard',
  shopkeeper: '/shopkeeper/dashboard',
  insurance: '/insurance/dashboard',
  afo: '/afo/dashboard',
  admin: '/bank/dashboard',
}

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true },
  },

  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { public: true },
  },
  
  {
    path: '/farmer/dashboard',
    name: 'farmer-dashboard',
    component: () => import('@/views/farmer/DashboardView.vue'),
    meta: { roles: ['smallholder', 'tenant'] },
  },
  {
    path: '/landowner/dashboard',
    name: 'landowner-dashboard',
    component: () => import('@/views/landowner/DashboardView.vue'),
    meta: { roles: ['landowner'] },
  },
  {
    path: '/bank/dashboard',
    name: 'bank-dashboard',
    component: () => import('@/views/bank/DashboardView.vue'),
    meta: { roles: ['bank', 'admin'] },
  },
  {
    path: '/factory/dashboard',
    name: 'factory-dashboard',
    component: () => import('@/views/factory/DashboardView.vue'),
    meta: { roles: ['factory'] },
  },
  {
    path: '/shopkeeper/dashboard',
    name: 'shopkeeper-dashboard',
    component: () => import('@/views/shopkeeper/DashboardView.vue'),
    meta: { roles: ['shopkeeper'] },
  },
  {
    path: '/insurance/dashboard',
    name: 'insurance-dashboard',
    component: () => import('@/views/insurance/DashboardView.vue'),
    meta: { roles: ['insurance'] },
  },
  {
    path: '/afo/dashboard',
    name: 'afo-dashboard',
    component: () => import('@/views/afo/DashboardView.vue'),
    meta: { roles: ['afo'] },
  },
  {
    path: '/',
    redirect: '/login',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.public) {
    if ((to.name === 'login' || to.name === 'register') && auth.isLoggedIn && auth.user) {
      return ROLE_HOME[auth.user?.role] || '/login'
    }
    return true
  }

  if (!auth.isLoggedIn) {
    return { name: 'login' }
  }

  if (!auth.user) {
    try {
      await auth.restoreSession()
    } catch {
      return { name: 'login' }
    }
    if (!auth.user) {
      return { name: 'login' }
    }
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    return ROLE_HOME[auth.user?.role] || '/login'
  }

  return true
})

export default router