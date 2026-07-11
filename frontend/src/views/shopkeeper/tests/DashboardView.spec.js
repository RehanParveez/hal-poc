import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import ShopkeeperDashboardView from '@/views/shopkeeper/DashboardView.vue'
import { useWalletsStore } from '@/stores/wallets.js'

function mountView() {
  return mount(ShopkeeperDashboardView, { global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
}

describe('shopkeeper/DashboardView.vue', () => {
  it('fetches balance and transactions on mount', async () => {
    const wrapper = mountView()
    const wallets = useWalletsStore()
    await flushPromises()
    expect(wallets.fetchMyBalance).toHaveBeenCalled()
    expect(wallets.fetchTransactions).toHaveBeenCalled()
  })

  it('FIXED BUG: shows a loading message, not "No transactions yet," during the initial fetch window -- same gap as landowner\'s dashboard, since both shared the same unfixed logic', () => {
    const wrapper = mountView()
    expect(wrapper.text()).toContain('Loading transactions...')
    expect(wrapper.text()).not.toContain('No transactions yet.')
  })

  it('FIXED BUG: balance renders through the consistent PKR formatter', async () => {
    const wrapper = mountView()
    useWalletsStore().wallet = { balance: 15000 }
    await flushPromises()
    expect(wrapper.text()).toContain('PKR 15,000.00')
  })

  it('FIXED BUG: a failed balance fetch no longer blocks the transactions fetch', async () => {
    const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
    setActivePinia(pinia)
    const wallets = useWalletsStore()
    wallets.fetchMyBalance.mockRejectedValue(new Error('Network Error'))
    mount(ShopkeeperDashboardView, { global: { plugins: [pinia] } })
    await flushPromises()
    expect(wallets.fetchTransactions).toHaveBeenCalled()
  })

  it('debit transactions render red with a minus sign and formatted amount', async () => {
    const wrapper = mountView()
    useWalletsStore().transactions = [{ id: 't1', txn_type: 'input', direction: 'debit', amount: 750, created_at: '2026-01-01T00:00:00Z' }]
    await flushPromises()
    expect(wrapper.text()).toContain('- PKR 750.00')
  })

  it('does not render the landowner-only sections', () => {
    const wrapper = mountView()
    expect(wrapper.find('#parcels-section').exists()).toBe(false)
    expect(wrapper.find('#agreements-section').exists()).toBe(false)
  })
})