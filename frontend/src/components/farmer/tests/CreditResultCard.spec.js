import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CreditResultCard from '@/components/farmer/CreditResultCard.vue'

describe('CreditResultCard', () => {
  it('shows the pending spinner state', () => {
    const wrapper = mount(CreditResultCard, { props: { creditCheck: { status: 'pending' } } })
    expect(wrapper.text()).toContain('being processed')
  })

  it('shows the approved state with the max limit formatted', () => {
    const wrapper = mount(CreditResultCard, {
      props: { creditCheck: { status: 'completed', is_eligible: true, max_approved_limit_pkr: 100000, risk_tier: 'low_risk' } },
    })
    expect(wrapper.text()).toContain('Credit Check Passed')
    expect(wrapper.text()).toContain('100,000')
  })

  it('shows a write-off-specific reason when rejected due to write-off history', () => {
    const wrapper = mount(CreditResultCard, {
      props: { creditCheck: { status: 'completed', is_eligible: false, ecib_status: 'write_off' } },
    })
    expect(wrapper.text()).toContain('written off')
  })

  it('shows an overdue-specific reason when rejected due to an overdue payment', () => {
    const wrapper = mount(CreditResultCard, {
      props: { creditCheck: { status: 'completed', is_eligible: false, ecib_status: 'overdue' } },
    })
    expect(wrapper.text()).toContain('overdue payment')
  })

  it('shows a default-history reason when that flag is set even without a matching ecib_status', () => {
    const wrapper = mount(CreditResultCard, {
      props: { creditCheck: { status: 'completed', is_eligible: false, ecib_status: 'regular', default_history_flag: true } },
    })
    expect(wrapper.text()).toContain('default was found')
  })

  it('shows the manual review state', () => {
    const wrapper = mount(CreditResultCard, { props: { creditCheck: { status: 'manual_review' } } })
    expect(wrapper.text()).toContain('Manual Review')
  })

  it('shows the failed state', () => {
    const wrapper = mount(CreditResultCard, { props: { creditCheck: { status: 'failed' } } })
    expect(wrapper.text()).toContain('Could Not Be Completed')
  })
})