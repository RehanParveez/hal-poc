import apiClient from './client.js'

export function listLoans(params) {
  return apiClient.get('/loans/applications/', { params })
}

export function getLoan(id) {
  return apiClient.get(`/loans/applications/${id}/`)
}

export function applyForLoan(payload) {
  return apiClient.post('/loans/applications/', payload)
}

export function approveLoan(id, payload) {
  return apiClient.patch(`/loans/applications/${id}/approve/`, payload)
}

export function rejectLoan(id, payload) {
  return apiClient.patch(`/loans/applications/${id}/reject/`, payload)
}

export function disburseLoan(id) {
  return apiClient.post(`/loans/applications/${id}/disburse/`)
}