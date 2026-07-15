import apiClient from './client.js'

export function listNumberdars(params) {
  return apiClient.get('/community/numberdars/', { params })
}
export function submitVerificationRequest(numberdarId) {
  return apiClient.post('/community/verification-requests/', { numberdar_id: numberdarId })
}
export function listMyVerificationRequests() {
  return apiClient.get('/community/verification-requests/')
}
export function listVerificationQueue(params) {
  return apiClient.get('/community/verification-requests/', { params })
}
export function approveVerification(id) {
  return apiClient.patch(`/community/verification-requests/${id}/approve/`)
}
export function rejectVerification(id, notes) {
  return apiClient.patch(`/community/verification-requests/${id}/reject/`, { notes })
}