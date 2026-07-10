import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import BrowseContracts from '@/components/farmer/BrowseContracts.vue'
import { useContractsStore } from '@/stores/contracts.js'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(BrowseContracts, { global: { plugins: [pinia] } })
  return { wrapper, contracts: useContractsStore(), loans: useLoansStore(), crops: useCropsStore(), notify: useNotificationsStore() }
}

describe('BrowseContracts.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows empty state with no open contracts', () => {
    const { wrapper, contracts } = mountComponent()
    contracts.openContracts = []
    expect(wrapper.text()).toContain('No open contracts available.')
  })

  it('resolves crop name and computes remaining kg correctly (Decimal-as-string subtraction is safe here)', async () => {
    const { wrapper, contracts, crops } = mountComponent()
    crops.cropTypes = [{ id: 'crop-1', name: 'Wheat', code: 'WHEAT' }]
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '10000.00', allocated_kg: '3000.00', delivery_deadline: '2027-01-01' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Wheat (WHEAT)')
    expect(wrapper.text()).toContain('Remaining: 7000 kg')
  })

  it('falls back to "Unknown crop" for an unresolved crop id', async () => {
    const { wrapper, contracts, crops } = mountComponent()
    crops.cropTypes = []
    contracts.openContracts = [{ id: 'c1', crop: 'missing', base_price_per_kg: '50.00', required_kg: '100.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Unknown crop')
  })

  it('skips fetchCropTypes on mount when crops are already loaded', () => {
    const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true, initialState: { crops: { cropTypes: [{ id: 'c1' }] } } })
    mount(BrowseContracts, { global: { plugins: [pinia] } })
    expect(useCropsStore().fetchCropTypes).not.toHaveBeenCalled()
  })

  it('blocks submit with no kg entered', async () => {
    const { wrapper, contracts, loans, notify } = mountComponent()
    loans.activeLoan = { id: 'loan-1' }
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '100.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(contracts.allocate).not.toHaveBeenCalled()
    expect(notify.showError).toHaveBeenCalledWith({ message: 'enter the committed kg amount first.' })
  })

  it('blocks submit with no active loan', async () => {
    const { wrapper, contracts, loans, notify } = mountComponent()
    loans.activeLoan = null
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '100.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    await wrapper.vm.$nextTick()
    await wrapper.find('input[type="number"]').setValue(50)
    await wrapper.find('button').trigger('click')
    expect(contracts.allocate).not.toHaveBeenCalled()
    expect(notify.showError).toHaveBeenCalledWith({ message: 'you need a disbursed loan before you can allocate to a contract.' })
  })

  it('FIXED: negative kg is now blocked instead of reaching the store', async () => {
    const { wrapper, contracts, loans } = mountComponent()
    loans.activeLoan = { id: 'loan-1' }
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '100.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    await wrapper.vm.$nextTick()
    await wrapper.find('input[type="number"]').setValue(-30)
    await wrapper.find('button').trigger('click')
    expect(contracts.allocate).not.toHaveBeenCalled()
  })

  it('submits with the correct contract, loan, and kg on a valid amount', async () => {
    const { wrapper, contracts, loans } = mountComponent()
    loans.activeLoan = { id: 'loan-1' }
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '1000.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    contracts.allocate.mockResolvedValue()
    await wrapper.vm.$nextTick()
    await wrapper.find('input[type="number"]').setValue(200)
    await wrapper.find('button').trigger('click')
    expect(contracts.allocate).toHaveBeenCalledWith('c1', 'loan-1', 200)
  })

  it('surfaces the real backend error on a rejected allocation (e.g. CONTRACT_FULLY_ALLOCATED)', async () => {
    const { wrapper, contracts, loans, notify } = mountComponent()
    loans.activeLoan = { id: 'loan-1' }
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '100.00', allocated_kg: '80.00', delivery_deadline: '2027-01-01' }]
    contracts.allocate.mockRejectedValue({ response: { data: { error: 'Contract has only 20.00 kg remaining.' } } })
    await wrapper.vm.$nextTick()
    await wrapper.find('input[type="number"]').setValue(50)
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith({ message: 'Contract has only 20.00 kg remaining.' })
  })

  it('KNOWN GAP: the kg input is not cleared after a successful allocation', async () => {
    const { wrapper, contracts, loans } = mountComponent()
    loans.activeLoan = { id: 'loan-1' }
    contracts.openContracts = [{ id: 'c1', crop: 'crop-1', base_price_per_kg: '50.00', required_kg: '1000.00', allocated_kg: '0.00', delivery_deadline: '2027-01-01' }]
    contracts.allocate.mockResolvedValue()
    await wrapper.vm.$nextTick()
    const input = wrapper.find('input[type="number"]')
    await input.setValue(200)
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(input.element.value).toBe('200')
  })
})