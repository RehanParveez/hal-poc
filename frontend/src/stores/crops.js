import { defineStore } from 'pinia'
import * as cropsApi from '@/api/crops.js'
import { useNotificationsStore } from './notifications.js'

function toNumber(value) {
  return value === null || value === undefined ? value : Number(value)
}

export const useCropsStore = defineStore('crops', {
  state: () => ({
    cropTypes: [],
    inputCaps: [],
    milestones: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchCropTypes() {
      this.isLoading = true
      this.error = null
      try {
        const res = await cropsApi.listCropTypes()
        this.cropTypes = res.data.results ?? res.data
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load crop types.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchInputCaps() {
      this.isLoading = true
      this.error = null
      try {
        const res = await cropsApi.listInputCaps()
        const raw = res.data.results ?? res.data
        this.inputCaps = raw.map((c) => ({ ...c, max_cost_per_acre: toNumber(c.max_cost_per_acre) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load input caps.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchMilestones() {
      this.isLoading = true
      this.error = null
      try {
        const res = await cropsApi.listMilestones()
        const raw = res.data.results ?? res.data
        this.milestones = raw.map((m) => ({ ...m, unlock_pct: toNumber(m.unlock_pct) }))
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to load milestones.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async createCropType(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await cropsApi.createCropType(payload)
        notify.showSuccess('Crop type created.')
        await this.fetchCropTypes()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to create crop type.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async setInputCap(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await cropsApi.setInputCap(payload)
        notify.showSuccess('Input cap saved.')
        await this.fetchInputCaps()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to save input cap.'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async setMilestone(payload) {
      const notify = useNotificationsStore()
      this.isLoading = true
      this.error = null
      try {
        await cropsApi.setMilestone(payload)
        notify.showSuccess('Milestone saved.')
        await this.fetchMilestones()
      } catch (err) {
        this.error = err.response?.data?.error ?? 'Failed to save milestone.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
  },
})