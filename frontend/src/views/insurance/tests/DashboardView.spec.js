import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import InsuranceDashboardView from '@/views/insurance/DashboardView.vue'
import { useInsuranceStore } from '@/stores/insurance.js'

function mountView(claims = [], policies = []) {
  return mount(InsuranceDashboardView, {
    global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true, initialState: { insurance: { claims, policies } } })] },
  })
}

describe('insurance/DashboardView.vue', () => {
  it('fetches claims and policies on mount', () => {
    mountView()
    const insurance = useInsuranceStore() 
    expect(insurance.fetchClaims).toHaveBeenCalled()
    expect(insurance.fetchPolicies).toHaveBeenCalled()
  })

  it('FIXED BUG: no longer flashes "No claims yet" due to the shared isLoading race -- now uses a local ref awaiting both fetches together', () => {
    const wrapper = mountView([])
    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.text()).not.toContain('No claims yet.')
  })

  it('FIXED BUG: policies section now shows a loading indicator -- it had none at all before', () => {
    const wrapper = mountView([], [])
    expect(wrapper.text()).toContain('Loading...')
  })

  it('both sections show their real empty states once loading completes', async () => {
    const wrapper = mountView([], [])
    await flushPromises()
    expect(wrapper.text()).toContain('No claims yet.')
    expect(wrapper.text()).toContain('No policies yet.')
  })

  it('shows the review form only for pending claims', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }, { id: 'c2', farmer_name: 'Bilal', claim_amount: 3000, status: 'approved' }])
    await flushPromises()
    expect(wrapper.findAll('input[type="number"]')).toHaveLength(1)
  })

  it('FIXED BUG: Approve is disabled at the default zero amount -- previously always clickable', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }])
    await flushPromises()
    const approveBtn = wrapper.findAll('button').find((b) => b.text() === 'Approve')
    expect(approveBtn.attributes('disabled')).toBeDefined()
    await wrapper.find('input[type="number"]').setValue(4000)
    expect(approveBtn.attributes('disabled')).toBeUndefined()
  })

  it('Reject stays enabled with the default amount, since rejection needs no approved_amount', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }])
    await flushPromises()
    expect(wrapper.findAll('button').find((b) => b.text() === 'Reject').attributes('disabled')).toBeUndefined()
  })

  it('calls reviewClaim with the entered amount and note', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }])
    await flushPromises()
    const insurance = useInsuranceStore()
    insurance.reviewClaim.mockResolvedValue({})
    await wrapper.find('input[type="number"]').setValue(4500)
    await wrapper.findAll('button').find((b) => b.text() === 'Approve').trigger('click')
    await flushPromises()
    expect(insurance.reviewClaim).toHaveBeenCalledWith('c1', 'approved', 4500, '')
  })

  it('FIXED BUG: a failed review shows an inline error instead of an unhandled rejection with no feedback', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }])
    await flushPromises()
    const insurance = useInsuranceStore()
    insurance.reviewClaim.mockRejectedValue({ response: { data: { error: 'the claim is already approved. cant review again.' } } })
    await wrapper.findAll('button').find((b) => b.text() === 'Reject').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('the claim is already approved. cant review again.')
  })

  it('FIXED BUG: buttons disable during submission, preventing a double review click', async () => {
    const wrapper = mountView([{ id: 'c1', farmer_name: 'Ali', claim_amount: 5000, status: 'pending' }])
    await flushPromises()
    const insurance = useInsuranceStore()
    let resolveFn
    insurance.reviewClaim.mockReturnValue(new Promise((r) => { resolveFn = r }))
    wrapper.findAll('button').find((b) => b.text() === 'Reject').trigger('click')
    await flushPromises()
    expect(wrapper.findAll('button').some((b) => b.text().includes('Submitting'))).toBe(true)
    resolveFn({})
  })
})