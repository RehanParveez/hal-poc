import { defineStore } from 'pinia'
import * as inputsApi from '@/api/inputs.js' 
import { useNotificationsStore } from './notifications.js'
import { useEscrowStore } from './escrow.js'

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
        const escrowStore = useEscrowStore()
        await escrowStore.fetchWallet(payload.escrow_id)
        return res.data
      } catch (err) {
        notify.showError(err.response?.data?.message ?? 'Payment failed.')
        throw err
        
      } finally {
        this.isSubmitting = false
      }
    },
  },
})