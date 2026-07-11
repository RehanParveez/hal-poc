import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import ParcelsList from '@/components/landowner/ParcelsList.vue'
import { useLandStore } from '@/stores/land.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(ParcelsList, { global: { plugins: [pinia] } })
  return { wrapper, land: useLandStore() }
}
function findByText(wrapper, text) { return wrapper.findAll('button').find((b) => b.text().includes(text)) }
async function openForm(wrapper) { await findByText(wrapper, 'Register Parcel').trigger('click') }

describe('ParcelsList.vue', () => {
  it('FIXED: shows a loading message instead of a false empty state', async () => {
    const { wrapper, land } = mountComponent()
    land.isLoading = true
    land.parcels = []
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Loading parcels...')
    expect(wrapper.text()).not.toContain('No parcels registered yet.')
  })

  it('shows Verified only for arazi_verified parcels', async () => {
    const { wrapper, land } = mountComponent()
    land.parcels = [
      { id: 'p1', parcel_ref: 'PR-1', district: 'Faisalabad', total_acres: '10.00', available_acres: '10.00', arazi_verified: true },
      { id: 'p2', parcel_ref: 'PR-2', district: 'Faisalabad', total_acres: '5.00', available_acres: '5.00', arazi_verified: false },
    ]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('.bg-green-100').length).toBe(1)
  })

  it('IMPROVED: blocks blank parcel_ref/district and zero total_acres', async () => {
    const { wrapper, land } = mountComponent()
    await openForm(wrapper)
    await findByText(wrapper, 'Save Parcel').trigger('click')
    expect(land.createParcel).not.toHaveBeenCalled()
  })

  it('submits, resets, and closes on success', async () => {
    const { wrapper, land } = mountComponent()
    land.createParcel.mockResolvedValue()
    await openForm(wrapper)
    await wrapper.find('input[placeholder^="Parcel Reference"]').setValue('KHEWAT-1')
    await wrapper.find('input[placeholder="District"]').setValue('Faisalabad')
    await wrapper.find('input[type="number"]').setValue(10)
    await findByText(wrapper, 'Save Parcel').trigger('click')
    await flushPromises()
    expect(land.createParcel).toHaveBeenCalledWith({ parcel_ref: 'KHEWAT-1', district: 'Faisalabad', tehsil: '', total_acres: 10 })
    expect(wrapper.find('input[placeholder^="Parcel Reference"]').exists()).toBe(false)
  })

  it('IMPROVED: now extracts ANY field error generically, not just two hardcoded field names', async () => {
    const { wrapper, land } = mountComponent()
    land.createParcel.mockRejectedValue({ response: { data: { some_backend_field: ['This field is required.'] } } })
    await openForm(wrapper)
    await wrapper.find('input[placeholder^="Parcel Reference"]').setValue('KHEWAT-1')
    await wrapper.find('input[placeholder="District"]').setValue('Faisalabad')
    await wrapper.find('input[type="number"]').setValue(10)
    await findByText(wrapper, 'Save Parcel').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('This field is required.')
  })
})