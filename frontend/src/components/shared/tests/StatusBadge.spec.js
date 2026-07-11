import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/shared/StatusBadge.vue'

describe('StatusBadge.vue', () => {
  it('FIXED BUG: "completed" now gets green styling -- previously fell through to gray, matching neither TenantAgreement nor CropContract\'s real status value', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'completed' } })
    expect(wrapper.classes()).toContain('bg-green-100')
    expect(wrapper.classes()).not.toContain('bg-gray-100')
  })

  it('"complete" (SettlementInvoice\'s real value) still renders green, unaffected by the fix', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'complete' } })
    expect(wrapper.classes()).toContain('bg-green-100')
  })

  it.each([
    ['submitted', 'bg-amber-100'], ['bank_approved', 'bg-blue-100'], ['disbursed', 'bg-green-100'], ['rejected', 'bg-red-100'],
    ['pending', 'bg-amber-100'], ['active', 'bg-green-100'],
    ['open', 'bg-blue-100'], ['allocated', 'bg-blue-100'],
    ['claimed', 'bg-blue-100'], ['expired', 'bg-gray-200'],
  ])('maps real backend status "%s" to %s', (status, expectedClass) => {
    const wrapper = mount(StatusBadge, { props: { status } })
    expect(wrapper.classes()).toContain(expectedClass)
  })

  it('an unrecognized status falls back to gray instead of crashing', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'some_future_status' } })
    expect(wrapper.classes()).toContain('bg-gray-100')
  })

  it('normalizes case and trims whitespace before lookup', () => {
    const wrapper = mount(StatusBadge, { props: { status: '  ACTIVE  ' } })
    expect(wrapper.classes()).toContain('bg-green-100')
  })

  it('replaces underscores with spaces in the displayed text', () => {
    const wrapper = mount(StatusBadge, { props: { status: 'bank_approved' } })
    expect(wrapper.text()).toBe('bank approved')
  })
})