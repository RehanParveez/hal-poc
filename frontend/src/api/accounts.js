import apiClient from './client.js'

export function listBanks() {
  return apiClient.get('/accounts/users/banks/')
}
export function listShopkeepers() {
  return apiClient.get('/accounts/users/shopkeepers/')
}