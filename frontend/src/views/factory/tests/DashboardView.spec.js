import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DashboardView from '@/views/factory/DashboardView.vue'
import { useDeliveryStore } from '@/stores/delivery.js'
import { useSettlementsStore } from '@/stores/settlements.js'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(DashboardView, { global: { plugins: [pinia] } })
  return { wrapper, delivery: useDeliveryStore(), settlements: useSettlementsStore(), notify: useNotificationsStore() }
}

const inTransitBatch = { id: 'batch-1', batch_kg: '500.00', expected_payout: '25000.00', status: 'in_transit' }
const receivedBatch = { id: 'batch-2', batch_kg: '300.00', expected_payout: '15000.00', status: 'received' }

describe('factory/DashboardView.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('fetches batches then invoices on mount', async () => {
    const { delivery, settlements } = mountComponent()
    await flushPromises()
    expect(delivery.fetchBatches).toHaveBeenCalled()
    expect(settlements.fetchInvoices).toHaveBeenCalled()
  })

  it('shows "Mark Received" only for in_transit batches', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [inTransitBatch]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('button').some((b) => b.text() === 'Mark Received')).toBe(true)
  })

  it('shows the grading form only for received batches', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [receivedBatch]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('button').some((b) => b.text() === 'Confirm Grade')).toBe(true)
  })

  it('THE headline crash fix: a batch added AFTER mount (e.g. via markReceived refresh) no longer crashes the grading form', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [inTransitBatch]
    await wrapper.vm.$nextTick()
    delivery.batches = [{ ...inTransitBatch, status: 'received' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('button').some((b) => b.text() === 'Confirm Grade')).toBe(true)
  })

  it('FIXED: markReceived failure now surfaces via showError', async () => {
    const { wrapper, delivery, notify } = mountComponent()
    delivery.batches = [inTransitBatch]
    delivery.markReceived.mockRejectedValue({ response: { data: { error: "only in_transit batches can be marked receiv." } } })
    await wrapper.vm.$nextTick()
    await wrapper.findAll('button').find((b) => b.text() === 'Mark Received').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith('only in_transit batches can be marked receiv.')
  })

  it('FIXED: blocks confirming a grade with none selected', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [receivedBatch]
    await wrapper.vm.$nextTick()
    await wrapper.findAll('button').find((b) => b.text() === 'Confirm Grade').trigger('click')
    expect(delivery.confirmGrade).not.toHaveBeenCalled()
  })

  it('FIXED: blocks a deduction percentage over 100', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [receivedBatch]
    await wrapper.vm.$nextTick()
    await wrapper.find('select').setValue('Grade B')
    await wrapper.find('input[type="number"]').setValue(150)
    await wrapper.findAll('button').find((b) => b.text() === 'Confirm Grade').trigger('click')
    expect(delivery.confirmGrade).not.toHaveBeenCalled()
  })

  it('submits a valid grade with the correct arguments', async () => {
    const { wrapper, delivery } = mountComponent()
    delivery.batches = [receivedBatch]
    delivery.confirmGrade.mockResolvedValue()
    await wrapper.vm.$nextTick()
    await wrapper.find('select').setValue('Grade A')
    await wrapper.find('input[type="number"]').setValue(5)
    await wrapper.findAll('button').find((b) => b.text() === 'Confirm Grade').trigger('click')
    expect(delivery.confirmGrade).toHaveBeenCalledWith('batch-2', 'Grade A', 5, '')
  })

  it('FIXED: confirmGrade rejection now surfaces via showError, not an unhandled rejection', async () => {
    const { wrapper, delivery, notify } = mountComponent()
    delivery.batches = [receivedBatch]
    delivery.confirmGrade.mockRejectedValue({ response: { data: { error: "cant confirm the grade on a batch with status 'grade_confirmed'." } } })
    await wrapper.vm.$nextTick()
    await wrapper.find('select').setValue('Grade A')
    await wrapper.findAll('button').find((b) => b.text() === 'Confirm Grade').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith("cant confirm the grade on a batch with status 'grade_confirmed'.")
  })

  it('only offers factory-settle for invoices with status "advanced"', async () => {
    const { wrapper, settlements } = mountComponent()
    settlements.invoices = [
      { id: 'inv-1', status: 'advanced', gross_payout: '10000.00' },
      { id: 'inv-2', status: 'pending', gross_payout: '5000.00' },
    ]
    await wrapper.vm.$nextTick()
    expect(wrapper.findAll('button').filter((b) => b.text() === 'Settle with Bank')).toHaveLength(1)
  })

  it('FIXED: a rejected factory settlement now surfaces via showError', async () => {
    const { wrapper, settlements, notify } = mountComponent()
    settlements.invoices = [{ id: 'inv-1', status: 'advanced', gross_payout: '10000.00' }]
    settlements.factorySettle.mockRejectedValue({ response: { data: { error: 'this invoice has already been process. or cant be settled.' } } })
    await wrapper.vm.$nextTick()
    await wrapper.find('button.bg-purple-700').trigger('click')
    await wrapper.vm.$nextTick()
    expect(notify.showError).toHaveBeenCalledWith('this invoice has already been process. or cant be settled.')
  })

  it('renders PostContractForm', () => {
    expect(mountComponent().wrapper.findComponent({ name: 'PostContractForm' }).exists()).toBe(true)
  })
})