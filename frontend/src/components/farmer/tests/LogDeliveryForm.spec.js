import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import LogDeliveryForm from '@/components/farmer/LogDeliveryForm.vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useDeliveryStore } from '@/stores/delivery.js'

function mountForm(allocations = []) {
  const wrapper = mount(LogDeliveryForm, { global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
  const contracts = useContractsStore()
  contracts.allocations = allocations
  return { wrapper, contracts }
}

describe('LogDeliveryForm.vue', () => {
  it('shows the empty state when there are no allocations', () => {
    const { wrapper } = mountForm([])
    expect(wrapper.text()).toContain('No contract allocations found.')
  })

  it('fetches allocations on mount', () => {
    const { contracts } = mountForm()
    expect(contracts.fetchMyAllocations).toHaveBeenCalled()
  })

  it('FIXED: weight input now has min="0", absent before', async () => {
    const { wrapper } = mountForm([{ id: 'a1', contract_crop_code: 'WHEAT', committed_kg: '100', delivered_kg: '0' }])
    await flushPromises()
    expect(wrapper.find('input[type="number"]').attributes('min')).toBe('0')
  })

  it('submit stays disabled with no allocation or weight selected', async () => {
    const { wrapper } = mountForm([{ id: 'a1', contract_crop_code: 'WHEAT', committed_kg: '100', delivered_kg: '0' }])
    await flushPromises()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('FIXED: submit stays disabled for a negative batch weight -- previously only zero/empty were blocked', async () => {
    const { wrapper } = mountForm([{ id: 'a1', contract_crop_code: 'WHEAT', committed_kg: '100', delivered_kg: '0' }])
    await flushPromises()
    await wrapper.find('select').setValue('a1')
    await wrapper.find('input[type="number"]').setValue(-15)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('FIXED: a rejected createBatch no longer goes unhandled -- isSubmitting resets and the form is preserved for retry', async () => {
    const { wrapper } = mountForm([{ id: 'a1', contract_crop_code: 'WHEAT', committed_kg: '100', delivered_kg: '0' }])
    const delivery = useDeliveryStore()
    delivery.createBatch.mockRejectedValue({ response: { data: { error: "cant deliver more than committed." } } })
    await flushPromises()
    await wrapper.find('select').setValue('a1')
    await wrapper.find('input[type="number"]').setValue(500)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.find('button').text()).toBe('Log Delivery')
    expect(wrapper.find('input[type="number"]').element.value).toBe('500')
  })
})