import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationsStore } from '@/stores/notifications.js'

describe('useNotificationsStore', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('current getter returns the first item in the queue, FIFO', () => {
    const store = useNotificationsStore()
    store.showSuccess('First')
    store.showSuccess('Second')
    expect(store.current.message).toBe('First')
  })

  it('current is null when the queue is empty', () => {
    const store = useNotificationsStore()
    expect(store.current).toBe(null)
  })

  it('FIXED BUG: showError now preserves a plain string message instead of discarding it as "Something went wrong"', () => {
    const store = useNotificationsStore()
    store.showError('You can only file a claim on your own policy.')
    expect(store.current.message).toBe('You can only file a claim on your own policy.')
  })

  it('showError extracts .message from a DRF-style error object', () => {
    const store = useNotificationsStore()
    store.showError({ message: 'Escrow balance insufficient.' })
    expect(store.current.message).toBe('Escrow balance insufficient.')
  })

  it('showError falls back through non_field_errors when no direct message exists', () => {
    const store = useNotificationsStore()
    store.showError({ non_field_errors: ['You are already allocated to this contract.'] })
    expect(store.current.message).toBe('You are already allocated to this contract.')
  })

  it('showError falls back to the generic message only when truly nothing usable is present', () => {
    const store = useNotificationsStore()
    store.showError({})
    expect(store.current.message).toBe('Something went wrong. Please try again.')
  })

  it('showError falls back to the generic message for null/undefined input', () => {
    const store = useNotificationsStore()
    store.showError(undefined)
    expect(store.current.message).toBe('Something went wrong. Please try again.')
  })

  it('showAFOError remaps the real backend field names to the component\'s expected shape', () => {
    const store = useNotificationsStore()
    store.showAFOError({ category: 'seed', afo_cap_total: '2000.00', already_spent: '1800.00', remaining_allowed: '200.00', requested_amount: '5000.00', message: 'Blocked.' })
    expect(store.current).toMatchObject({ type: 'afo-error', cap: '2000.00', spent: '1800.00', remaining: '200.00', requested: '5000.00' })
  })

  it('DOCUMENTS A GAP: showAFOError exists and works correctly, but is never called from any store shared in this conversation -- confirmed dead code until stores/inputs.js routes AFO_LIMIT_EXCEEDED to it explicitly', () => {
    const store = useNotificationsStore()
    store.showAFOError({ category: 'x', afo_cap_total: '1', already_spent: '1', remaining_allowed: '0', requested_amount: '1', message: 'x' })
    expect(store.current.type).toBe('afo-error')
  })

  it('dismiss removes a specific notification by id, leaving others intact', () => {
    const store = useNotificationsStore()
    const id1 = store.push({ type: 'success', message: 'One' })
    store.push({ type: 'success', message: 'Two' })
    store.dismiss(id1)
    expect(store.queue).toHaveLength(1)
    expect(store.current.message).toBe('Two')
  })

  it('dismissCurrent removes only the front of the queue', () => {
    const store = useNotificationsStore()
    store.showSuccess('First')
    store.showSuccess('Second')
    store.dismissCurrent()
    expect(store.current.message).toBe('Second')
  })
})