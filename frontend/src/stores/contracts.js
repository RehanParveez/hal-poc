import { defineStore } from 'pinia'
import * as contractsApi from '@/api/contracts.js'

export const useContractsStore = defineStore('contracts', {
  state: () => ({
    allocations: [],
    isLoading: false,
  }),
  actions: {
    async fetchMyAllocations() {
      this.isLoading = true
      try {
        const res = await contractsApi.listAllocations()
        this.allocations = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },
  },
})