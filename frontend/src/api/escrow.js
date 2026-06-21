import apiClient from './client.js'

export function getEscrowBalance(escrowId) {
  return apiClient.get(`/escrow/wallets/${escrowId}/balance/`)
}

export function getEscrowTransactions(escrowId, params) {
  return apiClient.get(`/escrow/wallets/${escrowId}/transactions/`, { params })
}

export function getAFOCaps(escrowId) {
  return apiClient.get(`/escrow/wallets/${escrowId}/afo_caps/`)
}

export function payShopkeeper(escrowId, payload) {
  return apiClient.post(`/escrow/wallets/${escrowId}/pay_shopkeeper/`, payload)
}