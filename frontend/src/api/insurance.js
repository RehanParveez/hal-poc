import apiClient from './client.js'

export function listPolicies(params) {
  return apiClient.get('/insurance/policies/', { params })
}
export function listClaims(params) {
  return apiClient.get('/insurance/claims/', { params })
}
export function fileClaim(payload) {
  return apiClient.post('/insurance/claims/', payload)
}
export function reviewClaim(id, payload) {
  return apiClient.patch(`/insurance/claims/${id}/review/`, payload)
}