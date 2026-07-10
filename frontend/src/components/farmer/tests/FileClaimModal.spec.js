import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import FileClaimModal from '@/components/farmer/FileClaimModal.vue'
import { useInsuranceStore } from '@/stores/insurance.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn })
  const wrapper = mount(FileClaimModal, { 
    global: { plugins: [pinia] } 
  })
  const insurance = useInsuranceStore(pinia)
  const notify = useNotificationsStore(pinia)
  return { wrapper, insurance, notify }
}

describe('FileClaimModal.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('FIXED: policy_id -- the field the backend actually needs -- is now required', async () => {
    const { wrapper, insurance } = mountComponent()
    await wrapper.find('input[placeholder="Enter Loan/Agreement ID"]').setValue('loan-1')
    await wrapper.find('select').setValue('heavy_rainfall_and_flood')
    await wrapper.find('input[type="number"]').setValue(50000)
    await wrapper.find('button.bg-red-600').trigger('click')
    expect(insurance.submitClaim).not.toHaveBeenCalled()
  })

  it('FIXED: claim_amount is now validated (the visual min="1" never fired without a <form>)', async () => {
    const { wrapper, insurance } = mountComponent()
    await wrapper.find('input[placeholder="Enter Loan/Agreement ID"]').setValue('loan-1')
    await wrapper.find('input[placeholder="Enter Policy ID (e.g. 1)"]').setValue('policy-1')
    await wrapper.find('select').setValue('heavy_rainfall_and_flood')
    await wrapper.find('button.bg-red-600').trigger('click')
    await flushPromises()
    expect(insurance.submitClaim).not.toHaveBeenCalled()
  })

  it('submits the correct payload once all required fields are valid', async () => {
    const { wrapper, insurance } = mountComponent()
    insurance.submitClaim.mockResolvedValue()
    await wrapper.find('input[placeholder="Enter Loan/Agreement ID"]').setValue('loan-1')
    await wrapper.find('input[placeholder="Enter Policy ID (e.g. 1)"]').setValue('policy-1')
    await wrapper.find('select').setValue('heavy_rainfall_and_flood')
    await wrapper.find('input[type="number"]').setValue(50000)
    await wrapper.find('button.bg-red-600').trigger('click')
    await flushPromises()
    expect(insurance.submitClaim).toHaveBeenCalledWith({ loan_id: 'loan-1', policy_id: 'policy-1', reason: 'heavy_rainfall_and_flood', claim_amount: 50000 })
  })

  it('THE headline fix: a rejection now surfaces via showError instead of an unhandled promise rejection', async () => {
    const { wrapper, insurance, notify } = mountComponent()
    insurance.submitClaim.mockRejectedValue({ response: { data: { message: 'cant file a claim on an expired policy.' } } })
    await wrapper.find('input[placeholder="Enter Loan/Agreement ID"]').setValue('loan-1')
    await wrapper.find('input[placeholder="Enter Policy ID (e.g. 1)"]').setValue('policy-1')
    await wrapper.find('select').setValue('heavy_rainfall_and_flood')
    await wrapper.find('input[type="number"]').setValue(50000)
    await wrapper.find('button.bg-red-600').trigger('click')
    await flushPromises()
    expect(notify.showError).toHaveBeenCalledWith('cant file a claim on an expired policy.')
    expect(wrapper.emitted('success')).toBeFalsy()
  })

  it('emits close on Cancel without touching the store', async () => {
    const { wrapper, insurance } = mountComponent()
    await wrapper.find('button.bg-slate-800').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
    expect(insurance.submitClaim).not.toHaveBeenCalled()
  })
})