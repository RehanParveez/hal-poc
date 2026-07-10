import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InsuranceBadge from '@/components/farmer/InsuranceBadge.vue'

describe('InsuranceBadge.vue', () => {
  it('renders Active/Claimed correctly', () => {
    expect(mount(InsuranceBadge, { props: { status: 'active' } }).text()).toContain('Active')
    expect(mount(InsuranceBadge, { props: { status: 'claimed' } }).text()).toContain('Claimed')
  })

  it('FIXED: "expired" -- a real InsurancePolicy.STATUS_CHOICES value -- is now mapped instead of falling through to Unknown', () => {
    const wrapper = mount(InsuranceBadge, { props: { status: 'expired' } })
    expect(wrapper.text()).toContain('Expired')
  })

  it('OPEN QUESTION: "pending" is a CLAIM status, not a real InsurancePolicy value -- kept for now, confirm intent', () => {
    const wrapper = mount(InsuranceBadge, { props: { status: 'pending' } })
    expect(wrapper.text()).toContain('Pending')
  })

  it('defaults to active with no prop', () => {
    expect(mount(InsuranceBadge).text()).toContain('Active')
  })
})