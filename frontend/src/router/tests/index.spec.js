import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth.js'
import * as authApi from '@/api/auth.js'
import router from '@/router/index.js'

vi.mock('@/api/auth.js')

describe('router/index.js navigation guards', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    sessionStorage.clear()
    localStorage.clear()
    await router.replace('/login')
  })

  it('redirects an unauthenticated user to login', async () => {
    useAuthStore().accessToken = null
    await router.push('/farmer/dashboard')
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('allows an authenticated farmer onto the farmer dashboard', async () => {
    const auth = useAuthStore()
    auth.accessToken = 'tok'
    auth.user = { role: 'smallholder' }
    await router.push('/farmer/dashboard')
    expect(router.currentRoute.value.name).toBe('farmer-dashboard')
  })

  it('redirects a wrong-role user to their own role home', async () => {
    const auth = useAuthStore()
    auth.accessToken = 'tok'
    auth.user = { role: 'shopkeeper' }
    await router.push('/bank/dashboard')
    expect(router.currentRoute.value.path).toBe('/shopkeeper/dashboard')
  })

  it('admin correctly lands on bank-dashboard (explicitly allowed there)', async () => {
    const auth = useAuthStore()
    auth.accessToken = 'tok'
    auth.user = { role: 'admin' }
    await router.push('/bank/dashboard')
    expect(router.currentRoute.value.name).toBe('bank-dashboard')
  })

  it('redirects an already-logged-in user away from /login', async () => {
    await router.push('/register') 
    const auth = useAuthStore()
    auth.accessToken = 'tok'
    auth.user = { role: 'factory' }
    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('factory-dashboard')
  })

  it('FIXED: an already-logged-in user is now also redirected away from /register', async () => {
    const auth = useAuthStore()
    auth.accessToken = 'tok'
    auth.user = { role: 'landowner' }
    await router.push('/register')
    expect(router.currentRoute.value.name).toBe('landowner-dashboard')
  })

  it('THE headline fix: a valid token with a not-yet-loaded user now resolves via restoreSession instead of bouncing to login', async () => {
    sessionStorage.setItem('accessToken', 'valid-token')
    localStorage.setItem('refreshToken', 'refresh-1')
    const auth = useAuthStore()
    auth.accessToken = 'valid-token'
    auth.user = null
    authApi.fetchProfile.mockResolvedValue({ data: { role: 'smallholder' } })
    await router.push('/farmer/dashboard')
    expect(router.currentRoute.value.name).toBe('farmer-dashboard')
  })

  it('still falls back to login if restoreSession ultimately fails', async () => {
    sessionStorage.setItem('accessToken', 'stale-token')
    localStorage.setItem('refreshToken', 'stale-refresh')
    const auth = useAuthStore()
    auth.accessToken = 'stale-token'
    auth.user = null
    authApi.fetchProfile.mockRejectedValue({ response: { status: 401 } })
    authApi.refreshToken.mockRejectedValue({ response: { data: {} } })
    await router.push('/farmer/dashboard')
    expect(router.currentRoute.value.name).toBe('login')
  })
})