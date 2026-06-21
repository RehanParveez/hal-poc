import { defineStore } from 'pinia'
import * as landApi from '@/api/land.js'
import { useNotificationsStore } from './notifications.js'

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
      try {
        const res = await landApi.listLands()
        this.parcels = res.data.results ?? res.data
      } finally {
        this.isLoading = false
      }
    },
    async createParcel(payload) {
      const notify = useNotificationsStore()
      await landApi.createLand(payload)
      notify.showSuccess('Land parcel registered successfully.')
      await this.fetchParcels()
    },
    async fetchAgreements() {
      const res = await landApi.listAgreements()
      this.agreements = res.data.results ?? res.data
    },
    async approveAgreement(id) {
      const notify = useNotificationsStore()
      const res = await landApi.approveAgreement(id)
      notify.showSuccess(res.data.message)
      await this.fetchAgreements()
    },
    async rejectAgreement(id, reason) {
      const notify = useNotificationsStore()
      const res = await landApi.rejectAgreement(id, reason)
      notify.showSuccess(res.data.message)
      await this.fetchAgreements()
    },
  },
})