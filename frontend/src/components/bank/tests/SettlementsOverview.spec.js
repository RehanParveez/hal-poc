import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SettlementsOverview from '@/components/bank/SettlementsOverview.vue'
import { useSettlementsStore } from '@/stores/settlements.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(SettlementsOverview, { global: { plugins: [pinia] } })
  return { wrapper, settlements: useSettlementsStore() }
}

describe('SettlementsOverview.vue', () => {
  it('fetches invoices on mount', () => {
    expect(mountComponent().settlements.fetchInvoices).toHaveBeenCalled()
  })

  it('FIXED: shows a loading message, not a false empty state, while isLoading is true', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.isLoading = true
    settlements.invoices = []
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Loading settlements...')
    expect(wrapper.text()).not.toContain('No settlements yet.')
  })

  it('renders gross_payout and truncated id', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = [{ id: 'inv-12345678-xyz', status: 'advanced', gross_payout: '100000.00' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('#inv-1234')
    expect(wrapper.text()).toContain('PKR 100000.00')
  })
})