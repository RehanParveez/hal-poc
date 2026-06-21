import apiClient from './client.js'

export function listLands(params) {
  return apiClient.get('/land/lands/', { params })
}
export function createLand(payload) {
  return apiClient.post('/land/lands/', payload)
}
export function listAgreements(params) {
  return apiClient.get('/land/agreements/', { params })
}
export function approveAgreement(id) {
  return apiClient.patch(`/land/agreements/${id}/approve/`)
}
export function rejectAgreement(id, reason) {
  return apiClient.patch(`/land/agreements/${id}/reject/`, { reason })
}