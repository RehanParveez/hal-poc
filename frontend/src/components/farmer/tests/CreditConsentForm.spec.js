import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import CreditConsentForm from '@/components/farmer/CreditConsentForm.vue'
import { useCreditStore } from '@/stores/credit.js'

describe('CreditConsentForm', () => {
  function mountForm() {
    return mount(CreditConsentForm, {
      props: { loanId: 'loan-1' },
      global: {
        plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
        mocks: {
          $t: (msg) => msg
        }
      },
    })
  }

  it('keeps the Send OTP button disabled until all three consents are checked', async () => {
    const wrapper = mountForm()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    for (const box of checkboxes) await box.setValue(true)
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('does not allow sending OTP with only two of the three boxes checked', async () => {
    const wrapper = mountForm()
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[0].setValue(true)
    await checkboxes[1].setValue(true)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('calls credit.requestOTP with the loanId prop when Send OTP is clicked', async () => {
    const wrapper = mountForm()
    const credit = useCreditStore()
    credit.requestOTP = vi.fn().mockResolvedValue()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    for (const box of checkboxes) await box.setValue(true)
    await wrapper.find('button').trigger('click')

    expect(credit.requestOTP).toHaveBeenCalledWith('loan-1')
  })

  it('emits consent-complete only after OTP verification succeeds', async () => {
    const wrapper = mountForm()
    const credit = useCreditStore()
    credit.requestOTP = vi.fn().mockResolvedValue()
    credit.verifyOTP = vi.fn().mockResolvedValue()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    for (const box of checkboxes) await box.setValue(true)
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    await wrapper.findComponent({ name: 'OTPInputField' }).vm.$emit('complete', '123456')
    expect(credit.verifyOTP).toHaveBeenCalledWith('123456')
    expect(wrapper.emitted('consent-complete')).toBeTruthy()
  })

  it('does not emit consent-complete when OTP verification fails', async () => {
    const wrapper = mountForm()
    const credit = useCreditStore()
    credit.requestOTP = vi.fn().mockResolvedValue()
    credit.verifyOTP = vi.fn().mockRejectedValue(new Error('wrong otp'))

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    for (const box of checkboxes) await box.setValue(true)
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    await wrapper.findComponent({ name: 'OTPInputField' }).vm.$emit('complete', '000000')
    expect(wrapper.emitted('consent-complete')).toBeFalsy()
  })
})