import apiClient from './client.js'

export function getEscrowBalance(id) {
  return apiClient.get(`/escrow/wallets/${id}/balance/`)
}

export function getAFOCaps(id) {
  return apiClient.get(`/escrow/wallets/${id}/afo_caps/`)
}

export function payShopkeeper(id, payload) {
  return apiClient.post(`/escrow/wallets/${id}/pay_shopkeeper/`, payload)
}