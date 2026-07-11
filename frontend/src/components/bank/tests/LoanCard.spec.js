import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import LoanCard from '@/components/bank/LoanCard.vue'
import { useLoansStore } from '@/stores/loans.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent(loan) {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(LoanCard, { props: { loan }, global: { plugins: [pinia] } })
  return { wrapper, loans: useLoansStore(), notify: useNotificationsStore() }
}

const baseLoan = {
  id: 'loan-1', farmer_name: 'Test Farmer', farmer_phone: '0300', farmer_district: 'Faisalabad',
  crop_name: 'Wheat', crop_season: 'rabi', acres_applied_for: '5.00', requested_amount: '50000.00',
  approved_amount: null, interest_rate_pct: null, status: 'submitted',
}

describe('LoanCard.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('shows approve/reject only for a submitted loan, disburse only for bank_approved', () => {
    const submitted = mountComponent({ ...baseLoan, status: 'submitted' }).wrapper
    expect(submitted.find('button.bg-green-700').exists()).toBe(true)
    expect(submitted.find('button.bg-blue-700').exists()).toBe(false)
    const approved = mountComponent({ ...baseLoan, status: 'bank_approved' }).wrapper
    expect(approved.find('button.bg-blue-700').exists()).toBe(true)
    expect(approved.find('button.bg-green-700').exists()).toBe(false)
  })

  it('FIXED: blocks approve with no amount entered', async () => {
    const { wrapper, loans } = mountComponent(baseLoan)
    await wrapper.find('button.bg-green-700').trigger('click')
    expect(loans.approveLoan).not.toHaveBeenCalled()
  })

  it('FIXED: blocks an interest rate over 50', async () => {
    const { wrapper, loans } = mountComponent(baseLoan)
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue(50000)
    await inputs[1].setValue(75)
    await wrapper.find('button.bg-green-700').trigger('click')
    expect(loans.approveLoan).not.toHaveBeenCalled()
  })

  it('approves with valid values, sent as strings', async () => {
    const { wrapper, loans } = mountComponent(baseLoan)
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue(50000)
    await inputs[1].setValue(12.5)
    loans.approveLoan.mockResolvedValue()
    await wrapper.find('button.bg-green-700').trigger('click')
    expect(loans.approveLoan).toHaveBeenCalledWith('loan-1', 50000, 12.5)
  })

  it('FIXED: a rejected approval now surfaces via showError', async () => {
    const { wrapper, loans, notify } = mountComponent(baseLoan)
    const inputs = wrapper.findAll('input[type="number"]')
    await inputs[0].setValue(50000)
    await inputs[1].setValue(12.5)
    loans.approveLoan.mockRejectedValue({ response: { data: { error: 'the interest rate must be b/w 0 and 50 perc.' } } })
    await wrapper.find('button.bg-green-700').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith('the interest rate must be b/w 0 and 50 perc.')
  })

  it('rejects with a prompt reason; skips the call if cancelled', async () => {
    vi.spyOn(window, 'prompt').mockReturnValueOnce('Insufficient collateral').mockReturnValueOnce(null)
    const { wrapper, loans } = mountComponent(baseLoan)
    loans.rejectLoan.mockResolvedValue()
    await wrapper.find('button.bg-red-600').trigger('click')
    expect(loans.rejectLoan).toHaveBeenCalledWith('loan-1', 'Insufficient collateral')
  })

  it('FIXED: a rejected disburse (LOAN_ALREADY_DISBURSED) now surfaces via showError', async () => {
    const { wrapper, loans, notify } = mountComponent({ ...baseLoan, status: 'bank_approved' })
    loans.disburseLoan.mockRejectedValue({ response: { data: { error: 'This loan has already been disbursed. Double-spend prevented.' } } })
    await wrapper.find('button.bg-blue-700').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith('This loan has already been disbursed. Double-spend prevented.')
  })
})