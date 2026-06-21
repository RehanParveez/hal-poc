import { defineStore } from 'pinia'
import * as escrowApi from '@/api/escrow.js'

export const useEscrowStore = defineStore('escrow', {
  state: () => ({
    wallet: null,
    caps: [],
    isLoading: false,
  }),
  getters: {
    spendableCategories: (state) => state.caps.filter((c) => c.is_allowed_now).map((c) => c.category),
  },
  actions: {
    async fetchWallet(escrowId) {
      this.isLoading = true
      try {
       const res = await escrowApi.getEscrowBalance(escrowId)
       this.wallet = res.data
      } finally {
        this.isLoading = false
      }
    },
    async refreshWallet(escrowId) {
      return this.fetchWallet(escrowId)
    },
    async fetchCaps(escrowId) {
      const res = await escrowApi.getAFOCaps(escrowId)
      this.caps = res.data.caps
    },
  },
})