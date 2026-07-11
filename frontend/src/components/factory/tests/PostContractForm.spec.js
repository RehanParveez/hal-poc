import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import PostContractForm from '@/components/factory/PostContractForm.vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useCropsStore } from '@/stores/crops.js'

function mountComponent(initialCrops = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]) {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true, initialState: { crops: { cropTypes: initialCrops } } })
  const wrapper = mount(PostContractForm, { global: { plugins: [pinia] } })
  return { wrapper, contracts: useContractsStore(), crops: useCropsStore() }
}

async function fillValid(wrapper) {
  await wrapper.find('select').setValue('crop-1')
  const n = wrapper.findAll('input[type="number"]')
  await n[0].setValue(5000)
  await n[1].setValue(120.5)
  await n[2].setValue(20)
  await wrapper.find('input[type="date"]').setValue('2027-01-01')
}

describe('PostContractForm.vue', () => {
  it('fetches crop types only when none are loaded', () => {
    expect(mountComponent([]).crops.fetchCropTypes).toHaveBeenCalled()
    expect(mountComponent().crops.fetchCropTypes).not.toHaveBeenCalled()
  })

  it('IMPROVED: blocks submit with no crop selected', async () => {
    const { wrapper, contracts } = mountComponent()
    await wrapper.find('button').trigger('click')
    expect(contracts.createContract).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Select a crop first.')
  })

  it('IMPROVED: blocks payment_defer_days outside the confirmed 1-30 range', async () => {
    const { wrapper, contracts } = mountComponent()
    await fillValid(wrapper)
    await wrapper.findAll('input[type="number"]')[2].setValue(45)
    await wrapper.find('button').trigger('click')
    expect(contracts.createContract).not.toHaveBeenCalled()
  })

  it('submits the correct payload; no factory field sent, server derives it', async () => {
    const { wrapper, contracts } = mountComponent()
    await fillValid(wrapper)
    contracts.createContract.mockResolvedValue()
    await wrapper.find('button').trigger('click')
    expect(contracts.createContract).toHaveBeenCalledWith({
      crop: 'crop-1', required_kg: 5000, base_price_per_kg: 120.5, payment_defer_days: 20,
      quality_grade_expected: 'Grade A', delivery_deadline: '2027-01-01',
    })
  })

  it('surfaces the first backend field error on rejection', async () => {
    const { wrapper, contracts } = mountComponent()
    await fillValid(wrapper)
    contracts.createContract.mockRejectedValue({ response: { data: { base_price_per_kg: ['the base price per kg s/h be > than zero.'] } } })
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('the base price per kg s/h be > than zero.')
  })

  it('CONFIRMED MATCHING BACKEND GAP: a past delivery_deadline is not blocked (backend accepts it too)', async () => {
    const { wrapper, contracts } = mountComponent()
    await fillValid(wrapper)
    await wrapper.find('input[type="date"]').setValue('2020-01-01')
    contracts.createContract.mockResolvedValue()
    await wrapper.find('button').trigger('click')
    expect(contracts.createContract).toHaveBeenCalled()
  })
})