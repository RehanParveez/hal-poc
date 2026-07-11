import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import LandownerDashboardView from '@/views/landowner/DashboardView.vue'
import { useWalletsStore } from '@/stores/wallets.js'

function mountView() {
  return mount(LandownerDashboardView, {
    global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })], stubs: { ParcelsList: true, AgreementsList: true } },
  })
}

describe('landowner/DashboardView.vue', () => {
  it('fetches balance and transactions on mount', async () => {
    const wrapper = mountView()
    const wallets = useWalletsStore()
    await flushPromises() 
    expect(wallets.fetchMyBalance).toHaveBeenCalled()
    expect(wallets.fetchTransactions).toHaveBeenCalled()
  })

  it('FIXED BUG: shows a loading message, not "No transactions yet," during the initial fetch window', () => {
    const wrapper = mountView()
    expect(wrapper.text()).toContain('Loading transactions...')
    expect(wrapper.text()).not.toContain('No transactions yet.')
  })

  it('shows "No transactions yet" only once loading truly completes', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('No transactions yet.')
  })

  it('FIXED BUG: balance renders through a consistent PKR formatter with separators and two decimals', async () => {
    const wrapper = mountView()
    useWalletsStore().wallet = { balance: 70000 }
    await flushPromises()
    expect(wrapper.text()).toContain('PKR 70,000.00')
  })

  it('FIXED BUG: transaction amounts are formatted consistently too, not raw-interpolated', async () => {
    const wrapper = mountView()
    useWalletsStore().transactions = [{ id: 't1', txn_type: 'batai_split', direction: 'credit', amount: 12500.5, created_at: '2026-01-01T00:00:00Z' }]
    await flushPromises()
    expect(wrapper.text()).toContain('+ PKR 12,500.50')
  })

  it('debit transactions render red with a minus sign', async () => {
    const wrapper = mountView()
    useWalletsStore().transactions = [{ id: 't2', txn_type: 'fee', direction: 'debit', amount: 50, created_at: '2026-01-01T00:00:00Z' }]
    await flushPromises()
    expect(wrapper.text()).toContain('- PKR 50.00')
  })

  it('FIXED BUG: a failed balance fetch no longer blocks the transactions fetch from running', async () => {
    const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
    setActivePinia(pinia)
    const wallets = useWalletsStore()
    wallets.fetchMyBalance.mockRejectedValue(new Error('Network Error'))
    mount(LandownerDashboardView, { global: { plugins: [pinia], stubs: { ParcelsList: true, AgreementsList: true } } })
    await flushPromises()
    expect(wallets.fetchTransactions).toHaveBeenCalled()
  })

  it('renders ParcelsList and AgreementsList sections', () => {
    const wrapper = mountView()
    expect(wrapper.findComponent({ name: 'ParcelsList' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'AgreementsList' }).exists()).toBe(true)
  })
})