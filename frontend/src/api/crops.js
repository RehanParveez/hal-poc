import apiClient from './client.js'

export function listCropTypes(params) {
  return apiClient.get('/crops/types/', { params })
}
export function createCropType(payload) {
  return apiClient.post('/crops/types/', payload)
}
export function listInputCaps(params) {
  return apiClient.get('/crops/inputcaps/', { params })
}
export function setInputCap(payload) {
  return apiClient.post('/crops/inputcaps/', payload)
}
export function listMilestones(params) {
  return apiClient.get('/crops/milestones/', { params })
}
export function setMilestone(payload) {
  return apiClient.post('/crops/milestones/', payload)
}