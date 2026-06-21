import { defineStore } from 'pinia'
import * as inputsApi from '@/api/inputs.js' 
import { useNotificationsStore } from './notifications.js'

export const useInputsStore = defineStore('inputs', {
  state: () => ({
    isSubmitting: false,
  }),
  actions: {
    async submitPayment(payload) {
      const notify = useNotificationsStore()
      this.isSubmitting = true
      try {
        const res = await inputsApi.submitInputPayment({
          escrow_id: payload.escrow_id,
          shopkeeper_id: payload.shopkeeper_id,
          input_category: payload.input_category,
          amount: payload.amount,
          item_description: payload.item_description || '',
        })
        notify.showSuccess(res.data.message)
        return res.data
      } finally {
        this.isSubmitting = false
      }
    },
  },
})