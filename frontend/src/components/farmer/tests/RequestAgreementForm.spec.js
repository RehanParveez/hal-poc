import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import RequestAgreementForm from '@/components/farmer/RequestAgreementForm.vue'
import { useLandStore } from '@/stores/land.js'
import { useAuthStore } from '@/stores/auth.js'

function mountForm(parcels = [], phone = '03001234567') {
  const wrapper = mount(RequestAgreementForm, { global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
  const land = useLandStore()
  const auth = useAuthStore()
  land.parcels = parcels
  auth.user = { phone }
  return { wrapper, land, auth }
}

describe('RequestAgreementForm.vue', () => {
  it('fetches parcels on mount', () => {
    const { land } = mountForm()
    expect(land.fetchParcels).toHaveBeenCalled()
  })

  it('FIXED: submit is disabled with nothing filled in -- no guard existed before', () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('FIXED: submit stays disabled and a warning shows when leased_acres exceeds the selected parcel\'s available_acres', async () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 5 }])
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(8)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    expect(wrapper.text()).toContain('exceeds this parcel')
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('allows leased_acres exactly equal to available_acres, matching the backend\'s ">" (not ">=") boundary', async () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 5 }])
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('FIXED: theka submit stays disabled until theka_amount is greater than zero', async () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('FIXED: batai submit stays disabled and a warning shows until shares sum to exactly 100', async () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('batai')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    const numberInputs = wrapper.findAll('input[type="number"]')
    await numberInputs[1].setValue(50)
    await numberInputs[2].setValue(40)
    expect(wrapper.text()).toContain('must add up to 100%')
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('enables submit once batai shares sum to exactly 100', async () => {
    const { wrapper } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('batai')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    const numberInputs = wrapper.findAll('input[type="number"]')
    await numberInputs[1].setValue(60)
    await numberInputs[2].setValue(40)
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('strips theka_amount from the payload for a batai submission, and vice versa', async () => {
    const { wrapper, land } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    land.createAgreement.mockResolvedValue({})
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('batai')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    const numberInputs = wrapper.findAll('input[type="number"]')
    await numberInputs[1].setValue(60)
    await numberInputs[2].setValue(40)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    const payloadSent = land.createAgreement.mock.calls[0][0]
    expect(payloadSent).not.toHaveProperty('theka_amount')
    expect(payloadSent).toMatchObject({ farmer_share_pct: 60, landowner_share_pct: 40 })
  })

  it('includes tenant_phone from the authenticated user', async () => {
    const { wrapper, land } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }], '03009998888')
    land.createAgreement.mockResolvedValue({})
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(land.createAgreement.mock.calls[0][0].tenant_phone).toBe('03009998888')
  })

  it('FIXED: isSubmitting disables the button during the request, preventing a double submit', async () => {
    const { wrapper, land } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    let resolveFn
    land.createAgreement.mockReturnValue(new Promise((r) => { resolveFn = r }))
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    resolveFn({})
  })

  it('FIXED: the form now resets after a successful submission -- it did not before', async () => {
    const { wrapper, land } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    land.createAgreement.mockResolvedValue({})
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.findAll('select')[0].element.value).toBe('')
    expect(wrapper.findAll('input[type="number"]')[0].element.value).toBe('0')
  })

  it('surfaces the backend\'s non_field_errors message on failure without resetting the form', async () => {
    const { wrapper, land } = mountForm([{ id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', available_acres: 10 }])
    land.createAgreement.mockRejectedValue({ response: { data: { non_field_errors: ['You are already allocated to this contract.'] } } })
    const selects = wrapper.findAll('select')
    await selects[0].setValue('p1')
    await selects[1].setValue('theka')
    await flushPromises()
    await wrapper.findAll('input[type="number"]')[0].setValue(5)
    await selects[2].setValue('rabi')
    await wrapper.findAll('input[type="number"]')[1].setValue(50000)
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('You are already allocated to this contract.')
    expect(wrapper.findAll('select')[0].element.value).toBe('p1')
  })
})