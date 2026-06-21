import apiClient from './client.js'

export function listInvoices(params) {
  return apiClient.get('/settlements/invoices/', { params })
}
export function getInvoice(id) {
  return apiClient.get(`/settlements/invoices/${id}/`)
}
export function factorySettle(id) {
  return apiClient.post(`/settlements/invoices/${id}/factory_settle/`)
}