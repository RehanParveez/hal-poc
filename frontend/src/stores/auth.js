import { defineStore } from 'pinia'
import * as authApi from '@/api/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: false,
    loginError: null,
    registerError: null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.accessToken,
    isFarmer: (state) => ['smallholder', 'tenant'].includes(state.user?.role),
    isLandowner: (state) => state.user?.role === 'landowner',
    isBankManager: (state) => state.user?.role === 'bank',
    isFactory: (state) => state.user?.role === 'factory',
    isShopkeeper: (state) => state.user?.role === 'shopkeeper',
    isInsuranceAgent: (state) => state.user?.role === 'insurance',
    isAFOOfficer: (state) => state.user?.role === 'afo',
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login(phone, password) {
      this.isLoading = true
      this.loginError = null
      try {
        const tokenRes = await authApi.login(phone, password)
        this.accessToken = tokenRes.data.access
        this.refreshToken = tokenRes.data.refresh
        sessionStorage.setItem('accessToken', this.accessToken)
        localStorage.setItem('refreshToken', this.refreshToken)

        const profileRes = await authApi.fetchProfile()
        this.user = profileRes.data

        return this.user
      } catch (err) {
        this.loginError = err.response?.data?.message || err.response?.data?.detail || 'The Login failed. Kindly check your phone and password.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async register(payload) {
      this.isLoading = true
      this.registerError = null
      try {
        const res = await authApi.register(payload)
        this.accessToken = res.data.access
        this.refreshToken = res.data.refresh
        this.user = res.data.user
        sessionStorage.setItem('accessToken', this.accessToken)
        localStorage.setItem('refreshToken', this.refreshToken)
        return this.user
      } catch (err) {
        this.registerError = err.response?.data?.message || err.response?.data?.detail || 'Registration failed.'
        throw err

      } finally {
        this.isLoading = false
      }
    },

    async refreshAccessToken() {
      const storedRefresh = this.refreshToken || localStorage.getItem('refreshToken')
      if (!storedRefresh) throw new Error('No refresh token available')
      const res = await authApi.refreshToken(storedRefresh)
      this.accessToken = res.data.access
      sessionStorage.setItem('accessToken', this.accessToken)
      if (res.data.refresh) {
        this.refreshToken = res.data.refresh
        localStorage.setItem('refreshToken', this.refreshToken)
      }
      return this.accessToken
    },

    async restoreSession() {
      const accessToken = sessionStorage.getItem('accessToken')
      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) return

      this.refreshToken = refreshToken
      if (accessToken) {
        this.accessToken = accessToken
      } else {
        try {
          await this.refreshAccessToken()
        } catch {
          this.logout()
          return
        }
      }

      try {
        const profileRes = await authApi.fetchProfile()
        this.user = profileRes.data
      } catch {
        try {
          await this.refreshAccessToken()
          const profileRes = await authApi.fetchProfile()
          this.user = profileRes.data
        } catch {
        this.logout()
      }
    }
  },

    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      sessionStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
  },
})