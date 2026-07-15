import { defineStore } from 'pinia'
import * as loansApi from '@/api/loans.js'
import { useNotificationsStore } from './notifications.js'

export const useLoansStore = defineStore('loans', {
  state: () => ({
    loans: [],
    activeLoan: null,
    isLoading: false,
    statusFilter: '',
    districtFilter: '',
    myLoans: [],
    error: null,
  }),

  getters: {
    pendingCreditCheckLoan: (state) =>
      state.myLoans.find((l) => l.status === 'bank_approved' && l.credit_check_status !== 'approved') || null,
  },

  actions: {
    async fetchAllMyLoans() {
      this.isLoading = true
      this.error = null
      try {
        const res = await loansApi.listLoans()
        this.myLoans = res.data.results ?? res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load loans.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async fetchLoans() {
      this.isLoading = true
      this.error = null
      try {
        const params = {}
        if (this.statusFilter) params.status = this.statusFilter
        if (this.districtFilter) params.district = this.districtFilter
        const res = await loansApi.listLoans(params)
        this.loans = res.data.results ?? res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load loans.'
        throw err

      } finally {
        this.isLoading = false
      }
    },

    async applyForLoan(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await loansApi.applyForLoan(payload)
        notify.showSuccess('Loan application submitted successfully.')
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to submit loan application.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

     async fetchMyLoan() {
      this.isLoading = true
      this.error = null
      try {
        const res = await loansApi.listLoans()
        const loans = res.data.results ?? res.data
        this.activeLoan = loans.find((l) => ['disbursed', 'repaid'].includes(l.status)) || null
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load your loan.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async approveLoan(id, approvedAmount, interestRatePct) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
       const res = await loansApi.approveLoan(id, {
        approved_amount: approvedAmount,
        interest_rate_pct: interestRatePct,
      })
       notify.showSuccess(res.data.message)
       await this.fetchLoans()
       return res.data.loan
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to approve loan.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async rejectLoan(id, reason) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        const res = await loansApi.rejectLoan(id, { rejection_reason: reason })
        notify.showSuccess(res.data.message)
        await this.fetchLoans()
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to reject loan.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async disburseLoan(id) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        const res = await loansApi.disburseLoan(id)
        notify.showSuccess(res.data.message)
        await this.fetchLoans()
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to disburse loan.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})