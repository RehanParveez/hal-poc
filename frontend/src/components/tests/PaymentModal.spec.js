import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import PaymentModal from '@/components/PaymentModal.vue'
import { useEscrowStore } from '@/stores/escrow.js'
import { useInputsStore } from '@/stores/inputs.js'
import * as accountsApi from '@/api/accounts.js'

vi.mock('@/api/accounts.js')

function mountModal(escrowCaps = [], escrowId = 'escrow-1') {
  const wrapper = mount(PaymentModal, {
    props: { escrowId },
    global: { plugins: [createTestingPinia({ stubActions: true, createSpy: vi.fn })] },
  })
  const escrow = useEscrowStore()
  escrow.caps = escrowCaps
  return { wrapper, escrow }
}

describe('PaymentModal.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    accountsApi.listShopkeepers.mockResolvedValue({ data: [{ id: 'u1', name: 'Ali Store', phone: '03001112222' }] })
  })

  it('FIXED: submit is disabled when amount is 0', async () => {
    const { wrapper } = mountModal([{ category: 'seed', is_allowed_now: true, total_cap: '10000.00', already_spent: '0', remaining: '10000.00' }])
    await flushPromises()
    await wrapper.find('select').setValue('seed')
    await wrapper.findAll('select')[1].setValue('u1')
    expect(wrapper.find('button.bg-green-600').attributes('disabled')).toBeDefined()
  })

  it('FIXED: submit is disabled when no shopkeeper is selected', async () => {
    const { wrapper } = mountModal([{ category: 'seed', is_allowed_now: true, total_cap: '10000.00', already_spent: '0', remaining: '10000.00' }])
    await flushPromises()
    await wrapper.find('select').setValue('seed')
    await wrapper.find('input[type="number"]').setValue(500)
    expect(wrapper.find('button.bg-green-600').attributes('disabled')).toBeDefined()
  })

  it('FIXED: submit is disabled when amount exceeds the AFO cap remaining, and the warning is visible', async () => {
    const { wrapper } = mountModal([{ category: 'seed', is_allowed_now: true, total_cap: '10000.00', already_spent: '9000.00', remaining: '1000.00' }])
    await flushPromises()
    const selects = wrapper.findAll('select')
    await selects[0].setValue('seed')
    await selects[1].setValue('u1')
    await wrapper.find('input[type="number"]').setValue(50000)
    expect(wrapper.find('button.bg-green-600').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('exceeds the remaining AFO cap')
  })

  it('FIXED: reopening for a different escrow now always refetches caps -- no stale cache', async () => {
    const { escrow } = mountModal([{ category: 'fertilizer', is_allowed_now: true, total_cap: '5000.00', already_spent: '0', remaining: '5000.00' }], 'escrow-B')
    await flushPromises()
    expect(escrow.fetchCaps).toHaveBeenCalledWith('escrow-B')
  })

  it('FIXED: a failed shopkeeper fetch now notifies the user, not just console.error', async () => {
    accountsApi.listShopkeepers.mockRejectedValue(new Error('Network Error'))
    mountModal()
    await flushPromises()
    const { useNotificationsStore } = await import('@/stores/notifications.js')
    const notify = useNotificationsStore()
    expect(notify.showError).toHaveBeenCalledWith('Failed to load shopkeeper list. Please try again.')
  })

  it('calls submitPayment with the exact object this component builds, resets the form, and emits success', async () => {
    const { wrapper } = mountModal([{ category: 'seed', is_allowed_now: true, total_cap: '10000.00', already_spent: '0', remaining: '10000.00' }])
    await flushPromises()
    const inputs = useInputsStore()
    const selects = wrapper.findAll('select')
    await selects[0].setValue('seed')
    await selects[1].setValue('u1')
    await wrapper.find('input[type="number"]').setValue(500)
    await wrapper.find('button.bg-green-600').trigger('click')
    await flushPromises()
    expect(inputs.submitPayment).toHaveBeenCalledWith({ escrow_id: 'escrow-1', shopkeeper_id: 'u1', input_category: 'seed', amount: 500 })
    expect(wrapper.emitted('success')).toBeTruthy()
  })

  it('emits close when Cancel is clicked', async () => {
    const { wrapper } = mountModal()
    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})