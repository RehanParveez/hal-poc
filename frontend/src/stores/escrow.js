import { defineStore } from 'pinia'
import * as escrowApi from '@/api/escrow.js'

export const useEscrowStore = defineStore('escrow', {
  state: () => ({
    wallet: null,
    caps: [],
    isLoading: false,
  }),
  actions: {
    async fetchWallet(id) {
      this.isLoading = true
      const res = await escrowApi.getEscrowBalance(id)
      this.wallet = res.data
      this.isLoading = false
    },
    async fetchCaps(id) {
      const res = await escrowApi.getAFOCaps(id)
      this.caps = res.data.caps
    }
  }
})