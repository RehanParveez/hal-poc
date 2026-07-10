import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import ApplyLoanForm from '@/components/farmer/ApplyLoanForm.vue'
import { useLoansStore } from '@/stores/loans.js'
import { useCropsStore } from '@/stores/crops.js'
import { useLandStore } from '@/stores/land.js'
import { useAuthStore } from '@/stores/auth.js'
import * as accountsApi from '@/api/accounts.js'

vi.mock('@/api/accounts.js')

function mountForm(role = 'smallholder') {
  const wrapper = mount(ApplyLoanForm, { global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
  const auth = useAuthStore()
  auth.user = { role }
  return wrapper
}

describe('ApplyLoanForm.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    accountsApi.listBanks.mockResolvedValue({ data: [{ id: 'b1', name: 'NRSP Bank' }] })
  })

  it('FIXED BUG: a failed banks fetch no longer blocks crop types from loading', async () => {
    accountsApi.listBanks.mockRejectedValue(new Error('Network Error'))
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    expect(crops.fetchCropTypes).toHaveBeenCalled()
  })

  it('FIXED BUG: a failed banks fetch no longer blocks tenant agreements from loading for a tenant', async () => {
    accountsApi.listBanks.mockRejectedValue(new Error('Network Error'))
    mountForm('tenant')
    await flushPromises()
    const land = useLandStore()
    expect(land.fetchAgreements).toHaveBeenCalled()
  })

  it('does not fetch agreements for a smallholder role', async () => {
    mountForm('smallholder')
    await flushPromises()
    const land = useLandStore()
    expect(land.fetchAgreements).not.toHaveBeenCalled()
  })

  it('FIXED: submit is disabled until bank, crop, and positive acres/amount are all set -- no guard existed before', async () => {
    const wrapper = mountForm()
    await flushPromises()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    await wrapper.find('select').setValue('b1')
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('FIXED: negative acres keeps submit disabled even with bank/crop/amount set', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(-5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('enables submit once every required field is valid', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('strips tenant_agreement from the payload when left blank', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    const loans = useLoansStore()
    loans.applyForLoan.mockResolvedValue({})
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    const payloadSent = loans.applyForLoan.mock.calls[0][0]
    expect(payloadSent).not.toHaveProperty('tenant_agreement')
  })

  it('FIXED: isSubmitting disables the button during the request, preventing a double submit', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    const loans = useLoansStore()
    let resolveFn
    loans.applyForLoan.mockReturnValue(new Promise((r) => { resolveFn = r }))
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    resolveFn({})
  })

  it('surfaces a custom_exception_handler-style message on failure', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    const loans = useLoansStore()
    loans.applyForLoan.mockRejectedValue({ response: { data: { error: 'ACREAGE_CEILING_EXCEEDED', message: 'Requested acres exceeds the parcel ceiling.' } } })
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Requested acres exceeds the parcel ceiling.')
  })

  it('FIXED: a generic per-field DRF validation error now surfaces instead of falling through to a useless generic message', async () => {
    const wrapper = mountForm()
    await flushPromises()
    const crops = useCropsStore()
    crops.cropTypes = [{ id: 'c1', name: 'Wheat', code: 'WHEAT' }]
    await flushPromises()
    const loans = useLoansStore()
    loans.applyForLoan.mockRejectedValue({ response: { data: { requested_amount: ['This field is required.'] } } })
    await wrapper.find('select').setValue('b1')
    await wrapper.findAll('select')[1].setValue('c1')
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('This field is required.')
  })
})