import apiClient from './client.js'

export function listMyNotifications(params) {
  return apiClient.get('/notifications/mine/', { params })
}
export function getUnreadCount() {
  return apiClient.get('/notifications/mine/unread_count/')
}
export function markRead(id) {
  return apiClient.patch(`/notifications/mine/${id}/mark_read/`)
}
export function markAllRead() {
  return apiClient.patch('/notifications/mine/mark_all_read/')
}