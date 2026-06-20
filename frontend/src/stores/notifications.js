import { defineStore } from 'pinia'

let nextId = 1

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    queue: [],
  }),
  getters: {
    current: (state) => state.queue[0] || null,
  },
  actions: {
    push(notification) {
      const id = nextId++
      this.queue.push({ id, ...notification })
      return id
    },
    showSuccess(message) {
      this.push({ type: 'success', message })
    },
    showError(data) {
      const message = data?.message || data?.detail || 'Something went wrong. Please try again.'
      this.push({ type: 'error', message, error: data?.error || null, raw: data })
    },
    showAFOError(data) {
      this.push({
        type: 'afo-error',
        category: data.category,
        cap: data.afo_cap_total,
        spent: data.already_spent,
        remaining: data.remaining_allowed,
        requested: data.requested_amount,
        message: data.message,
      })
    },
    dismiss(id) {
      this.queue = this.queue.filter((n) => n.id !== id)
    },
    dismissCurrent() {
      this.queue.shift()
    },
  },
})