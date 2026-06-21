import apiClient from './client.js'

export function submitInputPayment(payload) {
  return apiClient.post('/inputs/requests/', payload)
}

export function listInputRequests(params) {
  return apiClient.get('/inputs/requests/', { params })
}