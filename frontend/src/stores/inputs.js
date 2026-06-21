import { defineStore } from 'pinia'
import axios from 'axios' 
import { useNotificationsStore } from './notifications.js'

export const useInputsStore = defineStore('inputs', {
  state: () => ({
    afoState: { cap: 0, remaining: 0 },
  }),
  actions: {
    async submitPayment(payload) {
      const notify = useNotificationsStore()
      try {
        const res = await axios.post('/inputs/requests/', {
          escrow_id: payload.escrow_id,
          shopkeeper_id: payload.shopkeeper_id,
          input_category: payload.category,
          amount: payload.amount,
          item_description: payload.description
        })
        notify.showSuccess(res.data.message)
        return res.data
      } catch (error) {
        notify.showError(error.response?.data?.error || "Payment failed")
        throw error
      }
    },
    
    async fetchAFOCap(category, escrowId) {
    }
  }
})