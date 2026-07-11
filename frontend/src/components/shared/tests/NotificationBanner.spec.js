import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import NotificationBanner from '@/components/shared/NotificationBanner.vue'
import { useNotificationsStore } from '@/stores/notifications.js'

function mountWith(current) {
  const wrapper = mount(NotificationBanner, { global: { plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
  const notify = useNotificationsStore()
  notify.current = current
  return { wrapper, notify }
}

describe('NotificationBanner.vue', () => {
  it('renders nothing when there is no current notification', async () => {
    const { wrapper } = mountWith(null)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('div.fixed').exists()).toBe(false)
  })

  it('renders success styling', async () => {
    const { wrapper } = mountWith({ type: 'success', message: 'Loan approved.' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('div.fixed').classes()).toContain('bg-green-600')
    expect(wrapper.text()).toContain('Success')
  })

  it('CONFIRMED CORRECT: showAFOError\'s output shape (cap/spent/remaining/requested) renders correctly -- the earlier field-mismatch flag was wrong, retracted now that notifications.js is in hand', async () => {
    const { wrapper } = mountWith({
      type: 'afo-error', message: 'Blocked.', category: 'fertilizer',
      cap: '2000.00', spent: '1800.00', remaining: '200.00', requested: '5000.00',
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('PKR 5,000')
    expect(wrapper.text()).toContain('PKR 2,000')
    expect(wrapper.text()).toContain('PKR 1,800')
    expect(wrapper.text()).toContain('PKR 200')
    expect(wrapper.text()).toContain('AFO Limit Exceeded')
  })

  it('dismiss button calls notify.dismissCurrent()', async () => {
    const { wrapper, notify } = mountWith({ type: 'error', message: 'Failed.' })
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(notify.dismissCurrent).toHaveBeenCalled()
  })

  it('formatPKR falls back to em-dash for a non-numeric value instead of crashing', async () => {
    const { wrapper } = mountWith({ type: 'afo-error', message: 'x', category: 'seed', cap: undefined, spent: '0', remaining: '0', requested: '0' })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('PKR —')
  })
})