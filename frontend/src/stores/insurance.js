import { defineStore } from 'pinia'
import * as insuranceApi from '@/api/insurance.js'
import { useNotificationsStore } from './notifications.js'

export const useInsuranceStore = defineStore('insurance', {
  state: () => ({
    policies: [],
    claims: [],
    isLoading: false,
  }),
  actions: {
    async fetchPolicies(params) {
      this.isLoading = true
      try {
        const res = await insuranceApi.listPolicies(params)
        this.policies = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },
    async fetchClaims(params) {
      const res = await insuranceApi.listClaims(params)
      this.claims = res.data.results ?? res.data
    },
    async reviewClaim(id, decision, approvedAmount, reviewerNote) {
      const notify = useNotificationsStore()
      const payload = { decision, reviewer_note: reviewerNote }
      if (decision === 'approved') payload.approved_amount = approvedAmount
      await insuranceApi.reviewClaim(id, payload)
      notify.showSuccess('Claim reviewed successfully.')
      await this.fetchClaims()
    },
  },
})