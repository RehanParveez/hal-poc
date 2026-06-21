import { defineStore } from 'pinia'
import * as loansApi from '@/api/loans.js'
import { useNotificationsStore } from './notifications.js'

export const useLoansStore = defineStore('loans', {
  state: () => ({
    loans: [],
    isLoading: false,
    statusFilter: '',
    districtFilter: '',
  }),
  actions: {
    async fetchLoans() {
      this.isLoading = true
      try {
        const params = {}
        if (this.statusFilter) params.status = this.statusFilter
        if (this.districtFilter) params.district = this.districtFilter
        const res = await loansApi.listLoans(params)
        this.loans = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },

    async approveLoan(id, approvedAmount, interestRatePct) {
      const notify = useNotificationsStore()
      const res = await loansApi.approveLoan(id, {
        approved_amount: approvedAmount,
        interest_rate_pct: interestRatePct,
      })
      notify.showSuccess(res.data.message)
      await this.fetchLoans()
      return res.data.loan
    },

    async rejectLoan(id, reason) {
      const notify = useNotificationsStore()
      const res = await loansApi.rejectLoan(id, { rejection_reason: reason })
      notify.showSuccess(res.data.message)
      await this.fetchLoans()
      return res.data
    },

    async disburseLoan(id) {
      const notify = useNotificationsStore()
      const res = await loansApi.disburseLoan(id)
      notify.showSuccess(res.data.message)
      await this.fetchLoans()
      return res.data
    },
  },
})