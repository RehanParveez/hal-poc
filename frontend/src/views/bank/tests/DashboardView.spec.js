import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DashboardView from '@/views/bank/DashboardView.vue'
import { useLoansStore } from '@/stores/loans.js'
import { useAuthStore } from '@/stores/auth.js'

const pushMock = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: pushMock }) }))

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(DashboardView, { global: { plugins: [pinia] } })
  return { wrapper, loans: useLoansStore(), auth: useAuthStore() }
}

describe('bank/DashboardView.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('fetches loans on mount', () => {
    expect(mountComponent().loans.fetchLoans).toHaveBeenCalled()
  })

  it('shows loading state, not the empty message, while isLoading', async () => {
    const { wrapper, loans } = mountComponent()
    loans.isLoading = true
    loans.loans = []
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.text()).not.toContain('No loan applications found.')
  })

  it('renders one LoanCard per loan', async () => {
    const { wrapper, loans } = mountComponent()
    loans.loans = [{ id: 'l1', status: 'submitted' }, { id: 'l2', status: 'disbursed' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAllComponents({ name: 'LoanCard' })).toHaveLength(2)
  })

  it('FIXED: changing the status filter now calls fetchLoans with a plain params object, not a raw DOM Event', async () => {
    const { wrapper, loans } = mountComponent()
    await wrapper.find('select').setValue('bank_approved')
    const lastCall = loans.fetchLoans.mock.calls.at(-1)
    expect(lastCall[0]).not.toBeInstanceOf(Event)
    expect(lastCall[0]).toEqual({ status: 'bank_approved' })
  })

  it('sends undefined status (not empty string) when "All statuses" is selected', async () => {
    const { wrapper, loans } = mountComponent()
    await wrapper.find('select').setValue('')
    const lastCall = loans.fetchLoans.mock.calls.at(-1)
    expect(lastCall[0]).toEqual({ status: undefined })
  })

  it('FIXED: a visible logout button now exists and calls the already-defined handler', async () => {
    const { wrapper, auth } = mountComponent()
    const logoutBtn = wrapper.findAll('button').find((b) => b.text().includes('Logout'))
    expect(logoutBtn).toBeTruthy()
    await logoutBtn.trigger('click')
    expect(auth.logout).toHaveBeenCalled()
    expect(pushMock).toHaveBeenCalledWith('/login')
  })

  it('renders SettlementsOverview', () => {
    const { wrapper } = mountComponent()
    expect(wrapper.findComponent({ name: 'SettlementsOverview' }).exists()).toBe(true)
  })
})