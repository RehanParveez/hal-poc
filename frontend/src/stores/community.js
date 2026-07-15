import { defineStore } from 'pinia'
import * as communityApi from '@/api/community.js'
import { useNotificationsStore } from './notifications.js'

export const useCommunityStore = defineStore('community', {
  state: () => ({ numberdars: [], myRequests: [], queue: [], isLoading: false }),
  getters: {
    myLatestRequest: (state) => state.myRequests[0] ?? null,
    isVerificationPending: (state) => state.myRequests[0]?.status === 'pending',
    pendingQueueCount: (state) => state.queue.filter((r) => r.status === 'pending').length,
  },
  actions: {
    async fetchNumberdars(district) {
      this.isLoading = true
      try {
        const res = await communityApi.listNumberdars(district ? { district } : {})
        this.numberdars = res.data.results ?? res.data
      } finally { this.isLoading = false }
    },
    async fetchMyRequests() {
      this.isLoading = true
      try {
        const res = await communityApi.listMyVerificationRequests()
        this.myRequests = res.data.results ?? res.data
      } finally { this.isLoading = false }
    },
    async submitRequest(numberdarId) {
      const notify = useNotificationsStore()
      try {
        const res = await communityApi.submitVerificationRequest(numberdarId)
        notify.showSuccess('Verification request sent to your Numberdar.')
        await this.fetchMyRequests()
        return res.data
      } catch (err) {
        notify.showError(err.response?.data?.message ?? 'Failed to submit request.')
        throw err
      }
    },
    async fetchQueue(statusFilter) {
      this.isLoading = true
      try {
        const res = await communityApi.listVerificationQueue(statusFilter ? { status: statusFilter } : {})
        this.queue = res.data.results ?? res.data
      } finally { this.isLoading = false }
    },
    async approve(id) {
      const notify = useNotificationsStore()
      const res = await communityApi.approveVerification(id)
      notify.showSuccess(res.data.message)
      await this.fetchQueue()
      return res.data
    },
    async reject(id, notes) {
      const notify = useNotificationsStore()
      const res = await communityApi.rejectVerification(id, notes)
      notify.showSuccess('Request rejected.')
      await this.fetchQueue()
      return res.data
    },
  },
})