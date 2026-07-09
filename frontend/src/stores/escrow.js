import { defineStore } from 'pinia'
import * as escrowApi from '@/api/escrow.js'

export const useEscrowStore = defineStore('escrow', {
  state: () => ({
    wallet: null,
    caps: [],
    isLoading: false,
    error: null,
  }),
  getters: {
    spendableCategories: (state) => state.caps.filter((c) => c.is_allowed_now).map((c) => c.category),
    remainingBalance: (state) => Number(state.wallet?.remaining_balance ?? 0),
    totalFunded: (state) => Number(state.wallet?.total_funded ?? 0),
    totalSpent: (state) => Number(state.wallet?.total_spent_on_inputs ?? 0),
    spendPercent: (state) => state.wallet?.spend_percentage ?? 0,
    activePhase: (state) => state.wallet?.active_phase ?? null,
    milestones: (state) => state.wallet?.all_phases ?? [],
  },
  actions: {
    async fetchWallet(escrowId) {
      this.isLoading = true
      this.error = null
      try {
       const res = await escrowApi.getEscrowBalance(escrowId)
       this.wallet = res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load escrow wallet.'
        throw err

      } finally {
        this.isLoading = false
      }
    },
    async refreshWallet(escrowId) {
      return this.fetchWallet(escrowId)
    },
    async fetchCaps(escrowId) {
      this.isLoading = true
      this.error = null
      try {
      const res = await escrowApi.getAFOCaps(escrowId)
      this.caps = res.data.caps
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load AFO caps.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})