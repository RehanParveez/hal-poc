import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import LoanHistory from '@/components/farmer/LoanHistory.vue'
import { useLoansStore } from '@/stores/loans.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(LoanHistory, { global: { plugins: [pinia] } })
  return { wrapper, loans: useLoansStore() }
}

describe('LoanHistory.vue', () => {
  it('fetches all loans on mount', () => {
    const { loans } = mountComponent()
    expect(loans.fetchAllMyLoans).toHaveBeenCalled()
  })

  it('shows empty state with no loans', () => {
    const { wrapper, loans } = mountComponent()
    loans.myLoans = []
    expect(wrapper.text()).toContain('No loan applications yet.')
  })

  it('NEEDS StatusBadge.vue CONFIRMED: passes a DIFFERENT enum ("bank_approved") through the SAME shared badge as SettlementsList', async () => {
    const { wrapper, loans } = mountComponent()
    loans.myLoans = [{ id: 'l1', requested_amount: '10000.00', acres_applied_for: '2.00', status: 'bank_approved' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent({ name: 'StatusBadge' }).props('status')).toBe('bank_approved')
  })

  it('renders one row per loan', async () => {
    const { wrapper, loans } = mountComponent()
    loans.myLoans = [
      { id: 'l1', requested_amount: '10000.00', acres_applied_for: '2.00', status: 'submitted' },
      { id: 'l2', requested_amount: '20000.00', acres_applied_for: '4.00', status: 'rejected' },
    ]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAllComponents({ name: 'StatusBadge' })).toHaveLength(2)
  })
})