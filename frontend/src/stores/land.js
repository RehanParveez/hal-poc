import { defineStore } from 'pinia'
import * as landApi from '@/api/land.js'
import { useNotificationsStore } from './notifications.js'

function toNumber(value) {
  return value === null || value === undefined ? value : Number(value)
}

export const useLandStore = defineStore('land', {
  state: () => ({
    parcels: [],
    agreements: [],
    isLoading: false,
  }),
  getters: {
    pendingAgreements: (state) => state.agreements.filter((a) => a.status === 'pending'),
  },
  actions: {
    async fetchParcels() {
      this.isLoading = true
      this.error = null
      try {
        const res = await landApi.listLands()
        const raw = res.data.results ?? res.data
        this.parcels = raw.map((p) => ({ ...p, total_acres: toNumber(p.total_acres), available_acres: toNumber(p.available_acres) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load land parcels.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
    async createParcel(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await landApi.createLand(payload)
        notify.showSuccess('Land parcel registered successfully.')
        await this.fetchParcels()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to register land parcel.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
    
    async createAgreement(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await landApi.createAgreement(payload)
        notify.showSuccess('Tenant agreement request submitted.')
        await this.fetchAgreements()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to submit agreement request.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async fetchAgreements(params = {}) {
      this.isLoading = true
      this.error = null
      try {
        const res = await landApi.listAgreements(params)
        const raw = res.data.results ?? res.data
        this.agreements = raw.map((a) => ({ ...a, leased_acres: toNumber(a.leased_acres), theka_amount: toNumber(a.theka_amount),
          farmer_share_pct: toNumber(a.farmer_share_pct), landowner_share_pct: toNumber(a.landowner_share_pct) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load agreements.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async approveAgreement(id) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        const res = await landApi.approveAgreement(id)
        notify.showSuccess(res.data.message)
        await this.fetchAgreements()
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to approve agreement.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  
    async rejectAgreement(id, reason) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        const res = await landApi.rejectAgreement(id, reason)
        notify.showSuccess(res.data.message)
        await this.fetchAgreements()
        return res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to reject agreement.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})