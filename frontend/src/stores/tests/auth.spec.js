import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth.js'
import * as authApi from '@/api/auth.js'

vi.mock('@/api/auth.js')

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    sessionStorage.clear()
    localStorage.clear()
  })

  describe('role getters -- checked against the real 9-role User.ROLES enum', () => {
    it.each([
      ['smallholder', 'isFarmer'], ['tenant', 'isFarmer'], ['landowner', 'isLandowner'],
      ['bank', 'isBankManager'], ['factory', 'isFactory'], ['shopkeeper', 'isShopkeeper'],
      ['insurance', 'isInsuranceAgent'], ['afo', 'isAFOOfficer'], ['admin', 'isAdmin'],
    ])('role "%s" correctly flips %s true', (role, getterName) => {
      const store = useAuthStore()
      store.user = { role }
      expect(store[getterName]).toBe(true)
    })

    it('isLoggedIn reflects presence of an access token', () => {
      const store = useAuthStore()
      expect(store.isLoggedIn).toBe(false)
      store.accessToken = 'tok'
      expect(store.isLoggedIn).toBe(true)
    })
  })

  describe('login', () => {
    it('stores tokens and profile, persists to the correct storage each', async () => {
      authApi.login.mockResolvedValue({ data: { access: 'acc-1', refresh: 'ref-1' } })
      authApi.fetchProfile.mockResolvedValue({ data: { role: 'smallholder', full_name: 'Test Farmer' } })
      const store = useAuthStore()
      await store.login('03001234567', 'pass')
      expect(store.user.full_name).toBe('Test Farmer')
      expect(sessionStorage.getItem('accessToken')).toBe('acc-1')
      expect(localStorage.getItem('refreshToken')).toBe('ref-1')
    })

    it('sets loginError from the backend detail message on failure', async () => {
      authApi.login.mockRejectedValue({ response: { data: { detail: 'No active account found with the given credentials' } } })
      const store = useAuthStore()
      await expect(store.login('03001234567', 'wrong')).rejects.toBeTruthy()
      expect(store.loginError).toBe('No active account found with the given credentials')
      expect(store.accessToken).toBe(null)
    })

    it('resets a stale loginError at the start of a new attempt', async () => {
      const store = useAuthStore()
      store.loginError = 'stale error'
      authApi.login.mockResolvedValue({ data: { access: 'a', refresh: 'r' } })
      authApi.fetchProfile.mockResolvedValue({ data: { role: 'smallholder' } })
      await store.login('x', 'y')
      expect(store.loginError).toBe(null)
    })
  })

  describe('refreshAccessToken', () => {
    it('throws with no refresh token available anywhere', async () => {
      const store = useAuthStore()
      await expect(store.refreshAccessToken()).rejects.toThrow('No refresh token available')
    })

    it('FIXED: persists the rotated refresh token, not just the new access token', async () => {
      authApi.refreshToken.mockResolvedValue({ data: { access: 'new-access', refresh: 'new-rotated-refresh' } })
      const store = useAuthStore()
      store.refreshToken = 'old-refresh'
      await store.refreshAccessToken()
      expect(store.refreshToken).toBe('new-rotated-refresh')
      expect(localStorage.getItem('refreshToken')).toBe('new-rotated-refresh')
    })

    it('falls back to localStorage when state.refreshToken is empty', async () => {
      localStorage.setItem('refreshToken', 'from-storage')
      authApi.refreshToken.mockResolvedValue({ data: { access: 'a', refresh: 'r' } })
      const store = useAuthStore()
      await store.refreshAccessToken()
      expect(authApi.refreshToken).toHaveBeenCalledWith('from-storage')
    })
  })

  describe('restoreSession', () => {
    it('does nothing with no refresh token anywhere', async () => {
      const store = useAuthStore()
      await store.restoreSession()
      expect(authApi.fetchProfile).not.toHaveBeenCalled()
    })

    it('uses a present access token directly without refreshing first', async () => {
      sessionStorage.setItem('accessToken', 'still-valid')
      localStorage.setItem('refreshToken', 'ref-1')
      authApi.fetchProfile.mockResolvedValue({ data: { role: 'smallholder' } })
      const store = useAuthStore()
      await store.restoreSession()
      expect(authApi.refreshToken).not.toHaveBeenCalled()
      expect(store.user.role).toBe('smallholder')
    })

    it('refreshes first when no access token is present at all', async () => {
      localStorage.setItem('refreshToken', 'ref-1')
      authApi.refreshToken.mockResolvedValue({ data: { access: 'new', refresh: 'ref-2' } })
      authApi.fetchProfile.mockResolvedValue({ data: { role: 'bank' } })
      const store = useAuthStore()
      await store.restoreSession()
      expect(authApi.refreshToken).toHaveBeenCalledWith('ref-1')
    })

    it('FIXED: an expired-but-present access token now retries via refresh instead of logging out immediately', async () => {
      sessionStorage.setItem('accessToken', 'expired-access')
      localStorage.setItem('refreshToken', 'still-valid-refresh')
      authApi.fetchProfile
        .mockRejectedValueOnce({ response: { status: 401 } })
        .mockResolvedValueOnce({ data: { role: 'smallholder' } })
      authApi.refreshToken.mockResolvedValue({ data: { access: 'fresh-access', refresh: 'fresh-refresh' } })

      const store = useAuthStore()
      await store.restoreSession()

      expect(authApi.refreshToken).toHaveBeenCalledWith('still-valid-refresh')
      expect(store.user.role).toBe('smallholder')
      expect(store.accessToken).toBe('fresh-access')
    })

    it('logs out only if the retry after a successful refresh still fails', async () => {
      sessionStorage.setItem('accessToken', 'expired-access')
      localStorage.setItem('refreshToken', 'also-bad')
      authApi.fetchProfile.mockRejectedValue({ response: { status: 401 } })
      authApi.refreshToken.mockRejectedValue({ response: { data: {} } })
      const store = useAuthStore()
      await store.restoreSession()
      expect(store.user).toBe(null)
      expect(store.accessToken).toBe(null)
    })
  })

  describe('logout', () => {
    it('clears state and both storage locations', () => {
      const store = useAuthStore()
      store.user = { role: 'smallholder' }
      store.accessToken = 'a'
      sessionStorage.setItem('accessToken', 'a')
      localStorage.setItem('refreshToken', 'r')
      store.logout()
      expect(store.user).toBe(null)
      expect(sessionStorage.getItem('accessToken')).toBe(null)
      expect(localStorage.getItem('refreshToken')).toBe(null)
    })

    it('KNOWN GAP: never calls a backend endpoint to revoke the token', () => {
      const store = useAuthStore()
      store.logout()
      expect(authApi.login).not.toHaveBeenCalled()
    })
  })

  describe('register', () => {
    it('stores tokens and user -- ASSUMES UserViewSet.create() returns them, unconfirmed', async () => {
      authApi.register.mockResolvedValue({ data: { access: 'a', refresh: 'r', user: { role: 'smallholder' } } })
      const store = useAuthStore()
      await store.register({ phone: '0300', password: 'x' })
      expect(store.user.role).toBe('smallholder')
    })

    it('FIXED: registerError now exists and is set on failure, matching login\'s pattern', async () => {
      authApi.register.mockRejectedValue({ response: { data: { phone: ['user with this phone already exists.'] } } })
      const store = useAuthStore()
      await expect(store.register({ phone: '0300', password: 'x' })).rejects.toBeTruthy()
      expect(store.registerError).toBeTruthy()
    })
  })
})