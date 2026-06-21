import apiClient from './client.js'

export function getMyBalance() {
  return apiClient.get('/wallets/balances/my_balance/')
}

export function listTransactions(params) {
  return apiClient.get('/wallets/transactions/', { params })
}