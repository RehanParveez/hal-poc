import { defineStore } from 'pinia'
import * as deliveryApi from '@/api/delivery.js'
import { useNotificationsStore } from './notifications.js'

export const useDeliveryStore = defineStore('delivery', {
  state: () => ({
    batches: [],
    isLoading: false,
  }),
  actions: {
    async fetchBatches(params) {
      this.isLoading = true
      try {
        const res = await deliveryApi.listBatches(params)
        this.batches = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },
    async markReceived(batchId) {
      const notify = useNotificationsStore()
      const res = await deliveryApi.markReceived(batchId)
      notify.showSuccess(res.data.message)
      await this.fetchBatches()
    },

    async createBatch(allocationId, batchKg) {
      const notify = useNotificationsStore()
      await deliveryApi.createBatch({ allocation: allocationId, batch_kg: batchKg })
      notify.showSuccess('Delivery batch is logged.')
    },

    async confirmGrade(batchId, gradeReceived, gradeDeductionPct, gradeNotes) {
      const notify = useNotificationsStore()
      try {
       const res = await deliveryApi.confirmGrade(batchId, {
         grade_received: gradeReceived,
         grade_deduction_pct: gradeDeductionPct,
         grade_notes: gradeNotes,
        })
       notify.showSuccess(res.data.message)
       await this.fetchBatches()
    } catch (error) {
    console.error("Backend Error Details:", error.response?.data || error.message)
    notify.showError("Failed to confirm grade: " + (error.response?.data?.error || "Server error"))
  }
},
}, 
})