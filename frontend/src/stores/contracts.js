import { defineStore } from 'pinia'
import * as contractsApi from '@/api/contracts.js'
import { useNotificationsStore } from './notifications.js'

function toNumber(value) {
  return value === null || value === undefined ? value : Number(value)
}

export const useContractsStore = defineStore('contracts', {
  state: () => ({
    allocations: [],
    openContracts: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchMyAllocations() {
      this.isLoading = true
      this.error = null
      try {
        const res = await contractsApi.listAllocations()
        const raw = res.data.results ?? res.data
        this.allocations = raw.map((a) => ({ ...a, committed_kg: toNumber(a.committed_kg) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load allocations.'
        throw err

      } finally {
        this.isLoading = false
      }
    },
    async fetchOpenContracts(filters = {}) {       
      this.isLoading = true
      this.error = null
      try {
        const res = await contractsApi.listContracts({ status: 'open', ...filters })
        const raw = res.data.results ?? res.data
        this.openContracts = raw.map((c) => ({ 
          ...c, required_kg: toNumber(c.required_kg), allocated_kg: toNumber(c.allocated_kg), base_price_per_kg: toNumber(c.base_price_per_kg) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load open contracts.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async allocate(contractId, loanId, committedKg) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await contractsApi.allocateToContract(contractId, { loan_id: loanId, committed_kg: committedKg })
        notify.showSuccess('Contract allocation created successfully.')
        await this.fetchOpenContracts()
        await this.fetchMyAllocations()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to create allocation.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async createContract(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
       await contractsApi.createContract(payload)
       notify.showSuccess('Contract posted successfully.')
      await this.fetchOpenContracts()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to post contract.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})