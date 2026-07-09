import { defineStore } from 'pinia'
import * as walletsApi from '@/api/wallets.js'

export const useWalletsStore = defineStore('wallets', {
  state: () => ({
    wallet: null,
    transactions: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchMyBalance() {
      this.isLoading = true
      this.error = null
      try {
        const res = await walletsApi.getMyBalance()
        this.wallet = { ...res.data, balance: Number(res.data.balance) }
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load wallet balance.'
        throw err

      } finally {
        this.isLoading = false
      }
    },
    async fetchTransactions(params) {
      this.isLoading = true
      this.error = null
      try {
        const res = await walletsApi.listTransactions(params)
        const raw = res.data.results ?? res.data
        this.transactions = raw.map(t => ({
          ...t,
          amount: Number(t.amount)
        }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load transactions.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})