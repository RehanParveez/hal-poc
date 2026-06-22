import { defineStore } from 'pinia'
import * as cropsApi from '@/api/crops.js'
import { useNotificationsStore } from './notifications.js'

export const useCropsStore = defineStore('crops', {
  state: () => ({
    cropTypes: [],
    inputCaps: [],
    milestones: [],
  }),
  actions: {
    async fetchCropTypes() {
      const res = await cropsApi.listCropTypes()
      this.cropTypes = res.data.results ?? res.data
    },
    async fetchInputCaps() {
      const res = await cropsApi.listInputCaps()
      this.inputCaps = res.data.results ?? res.data
    },
    async fetchMilestones() {
      const res = await cropsApi.listMilestones()
      this.milestones = res.data.results ?? res.data
    },
    async createCropType(payload) {
      const notify = useNotificationsStore()
      await cropsApi.createCropType(payload)
      notify.showSuccess('Crop type created.')
      await this.fetchCropTypes()
    },
    async setInputCap(payload) {
      const notify = useNotificationsStore()
      await cropsApi.setInputCap(payload)
      notify.showSuccess('Input cap saved.')
      await this.fetchInputCaps()
    },
    async setMilestone(payload) {
      const notify = useNotificationsStore()
      await cropsApi.setMilestone(payload)
      notify.showSuccess('Milestone saved.')
      await this.fetchMilestones()
    },
  },
})