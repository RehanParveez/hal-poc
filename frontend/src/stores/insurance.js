import { defineStore } from 'pinia'
import * as insuranceApi from '@/api/insurance.js'
import { useNotificationsStore } from './notifications.js'

function toNumber(value) {
  return value === null || value === undefined ? value : Number(value)
}

export const useInsuranceStore = defineStore('insurance', {
  state: () => ({
    policies: [],
    claims: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchPolicies(params) {
      this.isLoading = true
      this.error = null
      try {
        const res = await insuranceApi.listPolicies(params)
        const raw = res.data.results ?? res.data
        this.policies = raw.map((p) => ({ ...p, coverage_amount: toNumber(p.coverage_amount), premium_amount: toNumber(p.premium_amount) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load insurance policies.'
        throw err

      } finally {
        this.isLoading = false
      }
    },
    async fetchClaims(params) {
      this.isLoading = true
      this.error = null
      try {
        const res = await insuranceApi.listClaims(params)
        const raw = res.data.results ?? res.data
        this.claims = raw.map((c) => ({ ...c, claim_amount: toNumber(c.claim_amount), approved_amount: toNumber(c.approved_amount) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load insurance claims.'
        throw err
        } finally {
        this.isLoading = false
      }
    },
  
    async submitClaim(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await insuranceApi.fileClaim(payload) 
        notify.showSuccess('insurance claim submitted successfully.')
        await this.fetchClaims()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to file claim.'
        notify.showError(this.error)
        throw err
      } finally {
        this.isLoading = false
      }
    },
    async reviewClaim(id, decision, approvedAmount, reviewerNote) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        const payload = { decision, reviewer_note: reviewerNote }
        if (decision === 'approved') payload.approved_amount = approvedAmount
        const res = await insuranceApi.reviewClaim(id, payload)
        notify.showSuccess('Claim reviewed successfully.')
        await this.fetchClaims()
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to review claim.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})