import { defineStore } from 'pinia'
import * as settlementsApi from '@/api/settlements.js'

export const useSettlementsStore = defineStore('settlements', {
  state: () => ({
    invoices: [],
    currentInvoice: null,
    isLoading: false,
  }),
  actions: {
    async fetchInvoices(params) {
      this.isLoading = true
      try {
        const res = await settlementsApi.listInvoices(params)
        this.invoices = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },
    async fetchInvoice(id) {
      const res = await settlementsApi.getInvoice(id)
      this.currentInvoice = res.data
    },
  },
})