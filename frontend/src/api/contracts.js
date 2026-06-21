import apiClient from './client.js'

export function listContracts(params) {
  return apiClient.get('/contracts/cropcontracts/', { params })
}
export function allocateToContract(contractId, payload) {
  return apiClient.post(`/contracts/cropcontracts/${contractId}/allocate/`, payload)
}
export function listAllocations(params) {
  return apiClient.get('/contracts/allocations/', { params })
}