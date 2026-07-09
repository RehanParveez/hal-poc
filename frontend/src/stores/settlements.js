import { defineStore } from 'pinia'
import * as settlementsApi from '@/api/settlements.js'
import { useNotificationsStore } from './notifications.js'

export const useSettlementsStore = defineStore('settlements', {
  state: () => ({
    invoices: [],
    currentInvoice: null,
    isLoading: false,
    isSettling: false,
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
      this.isLoading = true
      try {
        const res = await settlementsApi.getInvoice(id)
        this.currentInvoice = res.data
        this.currentInvoice = res.data
      } finally {
        this.isLoading = false
      }
    },
  
    async factorySettle(id) {
      const notify = useNotificationsStore()
      this.isSettling = true
      try {
        const res = await settlementsApi.factorySettle(id)
        notify.showSuccess(res.data.message)
        if (this.currentInvoice?.id === id) {
          this.currentInvoice = res.data.invoice
        }
        await this.fetchInvoices()
        return res.data
      } catch (err) {
        notify.showError(err.response?.data?.error ?? 'Settlement failed.')
        throw err
      } finally {
        this.isSettling = false
      }
    }
  },
})