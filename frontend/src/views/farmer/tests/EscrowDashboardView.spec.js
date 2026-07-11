import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import EscrowDashboardView from '@/views/farmer/EscrowDashboardView.vue'
import { useEscrowStore } from '@/stores/escrow.js'

function mountView({ activeLoan = null, wallet = null } = {}) {
  return mount(EscrowDashboardView, {
    global: {
      plugins: [createTestingPinia({
        createSpy: vi.fn, stubActions: true,
        initialState: { loans: { activeLoan }, escrow: { wallet }, auth: { isLoggedIn: true } },
      })],
      stubs: { EscrowBalanceCard: true, MilestoneProgressBar: true, PaymentModal: true },
    },
  })
}

describe('farmer/EscrowDashboardView.vue', () => {
  it('shows a loading state immediately after mount, before the fetch resolves', () => {
    expect(mountView().text()).toContain('Loading your escrow account')
  })

  it('FIXED BUG: no longer shows "No disbursed loan found yet" during the loading window', () => {
    const wrapper = mountView()
    expect(wrapper.text()).not.toContain('No disbursed loan found yet.')
  })

  it('shows "No disbursed loan found yet" once loading completes and there truly is no active loan', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('No disbursed loan found yet.')
  })

  it('FIXED BUG: shows an error state instead of a silent blank screen when a loan exists but the wallet failed to load', async () => {
    const wrapper = mountView({ activeLoan: { id: 'l1', escrow_id: 'e1' }, wallet: null })
    await flushPromises()
    expect(wrapper.text()).toContain('Could not load your escrow account')
  })

  it('renders the balance card and pay button once the wallet loads successfully', async () => {
    const wrapper = mountView({ activeLoan: { id: 'l1', escrow_id: 'e1' }, wallet: { remaining_balance: '5000.00' } })
    await flushPromises()
    expect(wrapper.findComponent({ name: 'EscrowBalanceCard' }).exists()).toBe(true)
    expect(wrapper.text()).toContain('Pay Shopkeeper')
  })

  it('clicking Pay Shopkeeper opens PaymentModal with the loan\'s escrow_id', async () => {
    const wrapper = mountView({ activeLoan: { id: 'l1', escrow_id: 'e1' }, wallet: { remaining_balance: '5000.00' } })
    await flushPromises()
    await wrapper.find('button').trigger('click')
    expect(wrapper.findComponent({ name: 'PaymentModal' }).props('escrowId')).toBe('e1')
  })

  it('handleSuccess refreshes the wallet and caps, closing the modal', async () => {
    const wrapper = mountView({ activeLoan: { id: 'l1', escrow_id: 'e1' }, wallet: { remaining_balance: '5000.00' } })
    await flushPromises()
    const escrow = useEscrowStore()
    await wrapper.find('button').trigger('click')
    await wrapper.findComponent({ name: 'PaymentModal' }).vm.$emit('success')
    await flushPromises()
    expect(escrow.refreshWallet).toHaveBeenCalledWith('e1')
    expect(escrow.fetchCaps).toHaveBeenCalledWith('e1')
    expect(wrapper.findComponent({ name: 'PaymentModal' }).exists()).toBe(false)
  })

  it('UNCONFIRMED: escrow_id field name on LoanApplication is assumed -- apps/loans/serializers.py never shared', async () => {
    const wrapper = mountView({ activeLoan: { id: 'l1', escrow_id: 'escrow-xyz' }, wallet: { remaining_balance: '1.00' } })
    await flushPromises()
    await wrapper.find('button').trigger('click')
    expect(wrapper.findComponent({ name: 'PaymentModal' }).props('escrowId')).toBe('escrow-xyz')
  })
})