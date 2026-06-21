import { defineStore } from 'pinia'
import * as settlementsApi from '@/api/settlements.js'
import { useNotificationsStore } from './notifications.js'

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
    async factorySettle(id) {
      const notify = useNotificationsStore()
      const res = await settlementsApi.factorySettle(id)
      notify.showSuccess(res.data.message)
      await this.fetchInvoices()
    }
  },
})