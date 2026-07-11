import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DashboardView from '@/views/afo/DashboardView.vue'
import { useCropsStore } from '@/stores/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(DashboardView, { global: { plugins: [pinia] } })
  return { wrapper, crops: useCropsStore(), notify: useNotificationsStore() }
}
function findByText(wrapper, text) { return wrapper.findAll('button').find((b) => b.text().includes(text)) }

describe('afo/DashboardView.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('fetches crop types, input caps, and milestones on mount', async () => {
    const { crops } = mountComponent()
    await flushPromises() 
    expect(crops.fetchCropTypes).toHaveBeenCalled()
    expect(crops.fetchInputCaps).toHaveBeenCalled()
    expect(crops.fetchMilestones).toHaveBeenCalled()
  })

  describe('crop type form', () => {
    it('FIXED: blocks submit with missing fields', async () => {
      const { wrapper, crops } = mountComponent()
      await findByText(wrapper, 'Add Crop Type').trigger('click')
      expect(crops.createCropType).not.toHaveBeenCalled()
    })

    it('submits and resets the form on success', async () => {
      const { wrapper, crops } = mountComponent()
      crops.createCropType.mockResolvedValue()
      await wrapper.find('input[placeholder="e.g. Maize"]').setValue('Maize')
      await wrapper.find('input[placeholder="e.g. MAIZE"]').setValue('MAIZE')
      await wrapper.find('#crop-types-section select').setValue('kharif')
      await findByText(wrapper, 'Add Crop Type').trigger('click')
      await wrapper.vm.$nextTick()
      expect(crops.createCropType).toHaveBeenCalledWith({ name: 'Maize', code: 'MAIZE', season: 'kharif' })
      expect(wrapper.find('input[placeholder="e.g. Maize"]').element.value).toBe('')
    })

    it('FIXED: a rejected creation now surfaces via showError', async () => {
      const { wrapper, crops, notify } = mountComponent()
      crops.createCropType.mockRejectedValue({ response: { data: { code: ['crop type with this code already exists.'] } } })
      await wrapper.find('input[placeholder="e.g. Maize"]').setValue('Wheat')
      await wrapper.find('input[placeholder="e.g. MAIZE"]').setValue('WHEAT')
      await wrapper.find('#crop-types-section select').setValue('rabi')
      await findByText(wrapper, 'Add Crop Type').trigger('click')
      await wrapper.vm.$nextTick()
      expect(notify.showError).toHaveBeenCalledWith('crop type with this code already exists.')
    })
  })

  describe('AFO cap form', () => {
    it('FIXED: blocks submit with missing required fields', async () => {
      const { wrapper, crops } = mountComponent()
      await findByText(wrapper, 'Save Cap').trigger('click')
      expect(crops.setInputCap).not.toHaveBeenCalled()
    })

    it('FIXED: blocks a zero max_cost_per_acre', async () => {
      const { wrapper, crops } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      await wrapper.vm.$nextTick()
      const selects = wrapper.findAll('#input-caps-section select')
      await selects[0].setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Multan"]').setValue('Multan')
      await selects[1].setValue('seed')
      await selects[2].setValue('rabi')
      await findByText(wrapper, 'Save Cap').trigger('click')
      expect(crops.setInputCap).not.toHaveBeenCalled()
    })

    it('submits with all valid fields', async () => {
      const { wrapper, crops } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      crops.setInputCap.mockResolvedValue()
      await wrapper.vm.$nextTick()
      const selects = wrapper.findAll('#input-caps-section select')
      await selects[0].setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Multan"]').setValue('Multan')
      await selects[1].setValue('seed')
      await selects[2].setValue('rabi')
      await wrapper.find('input[placeholder="Max Cost per Acre (PKR)"]').setValue(2000)
      await findByText(wrapper, 'Save Cap').trigger('click')
      expect(crops.setInputCap).toHaveBeenCalledWith({ crop: 'crop-1', district: 'Multan', input_category: 'seed', valid_season: 'rabi', max_cost_per_acre: 2000 })
    })

    it('FIXED: a rejected save now surfaces via showError', async () => {
      const { wrapper, crops, notify } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      crops.setInputCap.mockRejectedValue({ response: { data: { max_cost_per_acre: ['the max cost per acre must be > than zero.'] } } })
      await wrapper.vm.$nextTick()
      const selects = wrapper.findAll('#input-caps-section select')
      await selects[0].setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Multan"]').setValue('Multan')
      await selects[1].setValue('seed')
      await selects[2].setValue('rabi')
      await wrapper.find('input[placeholder="Max Cost per Acre (PKR)"]').setValue(500)
      await findByText(wrapper, 'Save Cap').trigger('click')
      await wrapper.vm.$nextTick()
      expect(notify.showError).toHaveBeenCalledWith('the max cost per acre must be > than zero.')
    })
  })

  describe('milestone form', () => {
    it('FIXED: blocks a zero unlock_pct', async () => {
      const { wrapper, crops } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      await wrapper.vm.$nextTick()
      await wrapper.find('#milestones-section select').setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Mid-Season Growth"]').setValue('Sowing')
      await findByText(wrapper, 'Save Milestone').trigger('click')
      expect(crops.setMilestone).not.toHaveBeenCalled()
    })

    it('FIXED: blocks unlock_pct over 100', async () => {
      const { wrapper, crops } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      await wrapper.vm.$nextTick()
      await wrapper.find('#milestones-section select').setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Mid-Season Growth"]').setValue('Sowing')
      await wrapper.find('input[placeholder="e.g. 40"]').setValue(150)
      await findByText(wrapper, 'Save Milestone').trigger('click')
      expect(crops.setMilestone).not.toHaveBeenCalled()
    })

    it('toggles a category checkbox correctly', async () => {
      const { wrapper } = mountComponent()
      const seedCheckbox = wrapper.find('input[type="checkbox"][value="seed"]')
      expect(seedCheckbox.element.checked).toBe(false)
      await seedCheckbox.setValue(true)
      expect(seedCheckbox.element.checked).toBe(true)
    })

    it('submits with valid fields and resets the form after success', async () => {
      const { wrapper, crops } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      crops.setMilestone.mockResolvedValue()
      await wrapper.vm.$nextTick()
      await wrapper.find('#milestones-section select').setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Mid-Season Growth"]').setValue('Sowing')
      await wrapper.find('input[placeholder="e.g. 40"]').setValue(30)
      await wrapper.find('input[type="checkbox"][value="seed"]').setValue(true)
      await findByText(wrapper, 'Save Milestone').trigger('click')
      await wrapper.vm.$nextTick()
      expect(crops.setMilestone).toHaveBeenCalledWith(expect.objectContaining({ crop: 'crop-1', phase_name: 'Sowing', unlock_pct: 30, allowed_input_categories: ['seed'] }))
      expect(wrapper.find('input[placeholder="e.g. Mid-Season Growth"]').element.value).toBe('')
    })

    it('FIXED: a rejected save now surfaces via showError', async () => {
      const { wrapper, crops, notify } = mountComponent()
      crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
      crops.setMilestone.mockRejectedValue({ response: { data: { unlock_pct: ['unlock perc must be b/w 0 & 100.'] } } })
      await wrapper.vm.$nextTick()
      await wrapper.find('#milestones-section select').setValue('crop-1')
      await wrapper.find('input[placeholder="e.g. Mid-Season Growth"]').setValue('Sowing')
      await wrapper.find('input[placeholder="e.g. 40"]').setValue(50)
      await findByText(wrapper, 'Save Milestone').trigger('click')
      await wrapper.vm.$nextTick()
      expect(notify.showError).toHaveBeenCalledWith('unlock perc must be b/w 0 & 100.')
    })
  })
})