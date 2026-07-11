import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils' 
import { createTestingPinia } from '@pinia/testing'
import AgreementsList from '@/components/landowner/AgreementsList.vue'
import { useLandStore } from '@/stores/land.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(AgreementsList, { global: { plugins: [pinia] } })
  return { wrapper, land: useLandStore(), notify: useNotificationsStore() }
}
function findByText(wrapper, text) { return wrapper.findAll('button').find((b) => b.text().includes(text)) }
async function openForm(wrapper) { await findByText(wrapper, 'New Agreement').trigger('click') }
async function fillBase(wrapper, { phone = '03001234567', parcelId = 'parcel-1', season = 'Kharif 2026' } = {}) {
  await wrapper.find('input[placeholder="Tenant Phone"]').setValue(phone)
  const s = wrapper.findAll('select')
  await s[0].setValue(parcelId)
  await s[2].setValue(season)
}

describe('AgreementsList.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('fetches parcels then agreements on mount', async () => {
    const { land } = mountComponent()
    await flushPromises() 
    expect(land.fetchParcels).toHaveBeenCalled()
    expect(land.fetchAgreements).toHaveBeenCalled()
  })

  it('IMPROVED: blocks submit with required fields blank', async () => {
    const { wrapper, land } = mountComponent()
    await openForm(wrapper)
    await findByText(wrapper, 'Save Agreement').trigger('click')
    expect(land.createAgreement).not.toHaveBeenCalled()
  })

  it('IMPROVED: blocks zero leased_acres', async () => {
    const { wrapper, land } = mountComponent()
    land.parcels = [{ id: 'parcel-1', parcel_ref: 'PR-1' }]
    await wrapper.vm.$nextTick()
    await openForm(wrapper)
    await fillBase(wrapper)
    await findByText(wrapper, 'Save Agreement').trigger('click')
    expect(land.createAgreement).not.toHaveBeenCalled()
  })

  it('IMPROVED: blocks a theka agreement with no theka_amount', async () => {
    const { wrapper, land } = mountComponent()
    land.parcels = [{ id: 'parcel-1', parcel_ref: 'PR-1' }]
    await wrapper.vm.$nextTick()
    await openForm(wrapper)
    await fillBase(wrapper)
    await wrapper.find('input[placeholder="Leased Acres"]').setValue(5)
    await findByText(wrapper, 'Save Agreement').trigger('click')
    expect(land.createAgreement).not.toHaveBeenCalled()
  })

  it('OPEN QUESTION -- UNCONFIRMED: sends tenant_phone verbatim; the real model has no such field, only a tenant FK id', async () => {
    const { wrapper, land } = mountComponent()
    land.parcels = [{ id: 'parcel-1', parcel_ref: 'PR-1' }]
    land.createAgreement.mockResolvedValue()
    await wrapper.vm.$nextTick()
    await openForm(wrapper)
    await fillBase(wrapper)
    await wrapper.find('input[placeholder="Leased Acres"]').setValue(5)
    await wrapper.find('input[placeholder="Theka Amount (PKR)"]').setValue(30000)
    await findByText(wrapper, 'Save Agreement').trigger('click')
    expect(land.createAgreement.mock.calls[0][0].tenant_phone).toBe('03001234567')
  })

  it('FIXED: a rejected creation now surfaces via showError', async () => {
    const { wrapper, land, notify } = mountComponent()
    land.parcels = [{ id: 'parcel-1', parcel_ref: 'PR-1' }]
    land.createAgreement.mockRejectedValue({ response: { data: { error: 'A tenant agreement for this parcel and season already exists.' } } })
    await wrapper.vm.$nextTick()
    await openForm(wrapper)
    await fillBase(wrapper)
    await wrapper.find('input[placeholder="Leased Acres"]').setValue(5)
    await wrapper.find('input[placeholder="Theka Amount (PKR)"]').setValue(30000)
    await findByText(wrapper, 'Save Agreement').trigger('click')
    await flushPromises()
    expect(notify.showError).toHaveBeenCalledWith('A tenant agreement for this parcel and season already exists.')
  })

  it('only shows Approve/Reject for pending agreements', async () => {
    const { wrapper, land } = mountComponent()
    land.agreements = [
      { id: 'a1', tenant_name: 'Farmer A', parcel_ref: 'PR-1', agreement_type: 'theka', leased_acres: '5.00', season: 'Kharif 2026', theka_amount: '30000.00', status: 'pending' },
      { id: 'a2', tenant_name: 'Farmer B', parcel_ref: 'PR-2', agreement_type: 'theka', leased_acres: '3.00', season: 'Kharif 2026', theka_amount: '20000.00', status: 'active' },
    ]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('button').filter((b) => b.text() === 'Approve').length).toBe(1)
  })

  it('FIXED: approve and reject now surface errors instead of failing silently', async () => {
    vi.spyOn(window, 'prompt').mockReturnValue('Terms not acceptable')
    const { wrapper, land, notify } = mountComponent()
    land.agreements = [{ id: 'a1', tenant_name: 'Farmer A', parcel_ref: 'PR-1', agreement_type: 'theka', leased_acres: '5.00', season: 'Kharif 2026', theka_amount: '30000.00', status: 'pending' }]
    land.approveAgreement.mockRejectedValue({ response: { data: { error: 'Agreement already approved.' } } })
    land.rejectAgreement.mockRejectedValue({ response: { data: { error: 'Cannot reject.' } } })
    
    await wrapper.vm.$nextTick()
    
    await findByText(wrapper, 'Approve').trigger('click')
    await flushPromises()
    expect(notify.showError).toHaveBeenCalledWith('Agreement already approved.')
    
    await findByText(wrapper, 'Reject').trigger('click')
    await flushPromises() 
    expect(notify.showError).toHaveBeenCalledWith('Cannot reject.')
  })
})