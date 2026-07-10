import { defineStore } from 'pinia'
import * as deliveryApi from '@/api/delivery.js'
import { useNotificationsStore } from './notifications.js'

export const useDeliveryStore = defineStore('delivery', {
  state: () => ({
    batches: [],
    isLoading: false,
    isMutating: false,
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
      this.isMutating = true
      try {
        const res = await deliveryApi.markReceived(batchId)
        notify.showSuccess(res.data.message)
        await this.fetchBatches()
        return res.data
      } catch (error) {
        notify.showError(error.response?.data?.error ?? 'Failed to mark batch received.')
        throw error
      } finally {
        this.isMutating = false
      }
    },

    async createBatch(allocationId, batchKg) {
      const notify = useNotificationsStore()
      this.isMutating = true
      try {
        const res = await deliveryApi.createBatch({ allocation: allocationId, batch_kg: batchKg })
        notify.showSuccess('Delivery batch is logged.')
        await this.fetchBatches()
        return res.data
      } catch (error) {
        notify.showError(error.response?.data?.error ?? 'Failed to log delivery batch.')
        throw error
      } finally {
        this.isMutating = false
      }
    },

    async confirmGrade(batchId, gradeReceived, gradeDeductionPct, gradeNotes) {
      const notify = useNotificationsStore()
      this.isMutating = true
      try {
       const res = await deliveryApi.confirmGrade(batchId, {
         grade_received: gradeReceived,
         grade_deduction_pct: gradeDeductionPct,
         grade_notes: gradeNotes,
        })
       notify.showSuccess(res.data.message)
       await this.fetchBatches()
       return res.data
    } catch (error) {
    console.error("Backend Error Details:", error.response?.data || error.message)
    notify.showError("Failed to confirm grade: " + (error.response?.data?.error || "Server error"))
    throw error
    } finally {
      this.isMutating = false
    }
   },
  },
})