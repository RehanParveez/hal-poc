import { defineStore } from 'pinia'
import * as walletsApi from '@/api/wallets.js'

export const useWalletsStore = defineStore('wallets', {
  state: () => ({
    wallet: null,
    transactions: [],
    isLoading: false,
  }),
  actions: {
    async fetchMyBalance() {
      this.isLoading = true
      try {
        const res = await walletsApi.getMyBalance()
        this.wallet = res.data
      } finally {
        this.isLoading = false
      }
    },
    async fetchTransactions(params) {
      const res = await walletsApi.listTransactions(params)
      this.transactions = res.data.results ?? res.data
    },
  },
})