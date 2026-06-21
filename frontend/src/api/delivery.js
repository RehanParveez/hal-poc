import apiClient from './client.js'

export function listBatches(params) {
  return apiClient.get('/delivery/batches/', { params })
}
export function markReceived(batchId) {
  return apiClient.patch(`/delivery/batches/${batchId}/mark_received/`)
}
export function confirmGrade(batchId, payload) {
  return apiClient.patch(`/delivery/batches/${batchId}/confirm_grade/`, payload)
}