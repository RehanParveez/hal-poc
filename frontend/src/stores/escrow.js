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
    remainingBalance: (state) => state.wallet?.remaining_balance ?? 0,
    totalFunded: (state) => state.wallet?.total_funded ?? 0,
    totalSpent: (state) => state.wallet?.total_spent_on_inputs ?? 0,
    spendPercent: (state) => state.wallet?.spend_percentage ?? 0,
    activePhase: (state) => state.wallet?.active_phase ?? null,
    milestones: (state) => state.wallet?.all_phases ?? [],
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