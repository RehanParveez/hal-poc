import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SettlementsList from '@/components/farmer/SettlementsList.vue'
import { useSettlementsStore } from '@/stores/settlements.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(SettlementsList, { global: { plugins: [pinia] } })
  return { wrapper, settlements: useSettlementsStore() }
}

describe('SettlementsList.vue', () => {
  it('fetches invoices on mount', () => {
    const { settlements } = mountComponent()
    expect(settlements.fetchInvoices).toHaveBeenCalled()
  })

  it('shows empty state with no invoices', () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = []
    expect(wrapper.text()).toContain('No settlements yet.')
  })

  it('truncates the invoice id to 8 chars and renders farmer_net_profit directly (safe, display-only)', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = [{ id: 'inv-12345678-abcd', status: 'complete', farmer_net_profit: '92000.00' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('#inv-1234')
    expect(wrapper.text()).toContain('PKR 92000.00')
  })

  it('fetches the detail invoice on row click', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = [{ id: 'inv-1', status: 'advanced', farmer_net_profit: '5000.00' }]
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(settlements.fetchInvoice).toHaveBeenCalledWith('inv-1')
  })

  it('renders WaterfallBreakdown only once currentInvoice is populated', async () => {
    const { wrapper, settlements } = mountComponent()
    expect(wrapper.findComponent({ name: 'WaterfallBreakdown' }).exists()).toBe(false)
    settlements.currentInvoice = { id: 'inv-1' }
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent({ name: 'WaterfallBreakdown' }).exists()).toBe(true)
  })

  it('NEEDS StatusBadge.vue CONFIRMED: passes settlement statuses (e.g. "factsettl") through with no local mapping', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = [{ id: 'inv-1', status: 'factsettl', farmer_net_profit: '0.00' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent({ name: 'StatusBadge' }).props('status')).toBe('factsettl')
  })
})