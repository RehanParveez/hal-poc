import { defineStore } from 'pinia'
import * as contractsApi from '@/api/contracts.js'
import { useNotificationsStore } from './notifications.js'

export const useContractsStore = defineStore('contracts', {
  state: () => ({
    allocations: [],
    openContracts: [],
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
    async fetchOpenContracts() {
      const res = await contractsApi.listContracts({ status: 'open' })
      this.openContracts = res.data.results ?? res.data
    },
    async allocate(contractId, loanId, committedKg) {
      const notify = useNotificationsStore()
      await contractsApi.allocateToContract(contractId, { loan_id: loanId, committed_kg: committedKg })
      notify.showSuccess('Contract allocation created successfully.')
      await this.fetchOpenContracts()
      await this.fetchMyAllocations()
    },
    async createContract(payload) {
      const notify = useNotificationsStore()
      await contractsApi.createContract(payload)
      notify.showSuccess('Contract posted successfully.')
    },
  },
})