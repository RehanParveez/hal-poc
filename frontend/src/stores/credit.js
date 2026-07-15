import { defineStore } from 'pinia'
import * as creditApi from '@/api/credit.js'
import { useNotificationsStore } from './notifications.js'

const POLL_INTERVAL_MS = Number(import.meta.env.VITE_CREDIT_CHECK_POLL_INTERVAL_MS || 3000)
const TERMINAL_STATUSES = ['completed', 'failed', 'manual_review']

export const useCreditStore = defineStore('credit', {
  state: () => ({
    activeCheck: null, checks: [], otpReference: null,
    isRequestingOTP: false, isVerifyingOTP: false, isRunningCheck: false, pollIntervalId: null,
  }),
  getters: {
    isApproved: (state) => state.activeCheck?.status === 'completed' && state.activeCheck?.is_eligible === true,
    isRejected: (state) => state.activeCheck?.status === 'completed' && state.activeCheck?.is_eligible === false,
  },
  actions: {
    async requestOTP(loanId) {
      const notify = useNotificationsStore()
      this.isRequestingOTP = true
      try {
        const res = await creditApi.requestConsentOTP(loanId)
        this.otpReference = res.data.otp_reference
        notify.showSuccess('OTP sent to your registered phone number.')
      } finally { this.isRequestingOTP = false }
    },
    async verifyOTP(otpCode) {
      const notify = useNotificationsStore()
      this.isVerifyingOTP = true
      try {
        await creditApi.verifyConsentOTP(this.otpReference, otpCode)
        notify.showSuccess('Consent verified. You can now proceed.')
      } finally { this.isVerifyingOTP = false }
    },
    async runCreditCheck(loanId) {
      this.isRunningCheck = true
      try {
        const res = await creditApi.triggerCreditCheck(this.otpReference, loanId)
        this.activeCheck = res.data
        this.startPolling(res.data.id)
      } finally { this.isRunningCheck = false }
    },
    startPolling(checkId) {
      this.stopPolling()
      this.pollIntervalId = setInterval(() => this.pollStatus(checkId), POLL_INTERVAL_MS)
    },
    async pollStatus(checkId) {
      const res = await creditApi.pollCreditCheckStatus(checkId)
      this.activeCheck = res.data
      if (TERMINAL_STATUSES.includes(res.data.status)) this.stopPolling()
    },
    stopPolling() {
      if (this.pollIntervalId) { clearInterval(this.pollIntervalId); this.pollIntervalId = null }
    },
    async fetchHistory() {
      const res = await creditApi.listCreditChecks()
      this.checks = res.data.results ?? res.data
      return this.checks
    },
    async fetchByLoan(loanId) {
      const res = await creditApi.listCreditChecks({ loan_application: loanId })
      const results = res.data.results ?? res.data
      return results[0] ?? null
    },
  },
})