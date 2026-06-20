import axios from 'axios'
import { useAuthStore } from '@/stores/auth.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

let isRefreshing = false
let refreshQueue = []

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const notify = useNotificationsStore()
    const originalRequest = error.config

    if (!error.response) {
      notify.showError({ message: 'Network error — check your connection or that the backend server is running.' })
      return Promise.reject(error)
    }

    const { status, data } = error.response

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        })
      }
      isRefreshing = true
      try {
        const newToken = await auth.refreshAccessToken()
        refreshQueue.forEach((p) => p.resolve(newToken))
        refreshQueue = []
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        refreshQueue.forEach((p) => p.reject(refreshError))
        refreshQueue = []
        auth.logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (data?.error === 'AFO_LIMIT_EXCEEDED') {
      notify.showAFOError(data)
    } else if (status === 400) {
      notify.showError(data)
    } else if ([403, 409, 503].includes(status) || status >= 500) {
      notify.showError(data || { message: 'Something went wrong.' })
    }

    return Promise.reject(error)
  }
)

export default apiClient