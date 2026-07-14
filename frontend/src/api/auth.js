import apiClient from './client.js'

export function login(phone, password) {
  return apiClient.post('/accounts/tokenobtainpair/', { phone, password })
}

export function refreshToken(refresh) {
  return apiClient.post('/accounts/tokenrefresh/', { refresh })
}

export function register(payload) {
  return apiClient.post('/accounts/users/', payload)
}

export function fetchProfile() {
  return apiClient.get('/accounts/users/profile/')
}

export function updateProfile(payload) {
  return apiClient.patch('/accounts/users/profile/', payload)
}