import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import WaterfallBreakdown from '@/components/farmer/WaterfallBreakdown.vue'
 
function makeInvoice(overrides = {}) {
  return {
    batch_kg: '500.00', crop_name: 'Wheat', grade_received: 'Grade A', grade_deduction_pct: '0.00',
    expected_payout: '50000.00', gross_payout: '50000.00',
    principal: '10000.00', interest: '200.00', bank_commission: '490.00', platform_fee: '245.00',
    theka_payment: '0.00', batai_landowner_share: '0.00',
    farmer_net: '39065.00', insurance_triggered: false, bank_advanced_at: '2026-07-01T10:30:00Z',
    ...overrides,
  }
}
 
function mountBreakdown(invoice) {
  return mount(WaterfallBreakdown, { props: { invoice } })
}
 
describe('WaterfallBreakdown', () => {
  it('renders every settlement row against the real invoice field names', () => {
    const wrapper = mountBreakdown(makeInvoice())
    expect(wrapper.text()).toContain('₨ 10,000')
    expect(wrapper.text()).toContain('₨ 200')
    expect(wrapper.text()).toContain('₨ 490')
    expect(wrapper.text()).toContain('₨ 245')
  })
 
  it('renders the net profit from farmer_net, not a field that does not exist on the invoice', () => {
    const wrapper = mountBreakdown(makeInvoice({ farmer_net: '39065.00' }))
    expect(wrapper.text()).toContain('₨ 39,065')
  })
 
  it('shows the theka rent row only when theka_payment is greater than zero', () => {
    const withTheka = mountBreakdown(makeInvoice({ theka_payment: '3000.00' }))
    expect(withTheka.text()).toContain('Theka Rent (Landowner)')
    const withoutTheka = mountBreakdown(makeInvoice({ theka_payment: '0.00' }))
    expect(withoutTheka.text()).not.toContain('Theka Rent (Landowner)')
  })
 
  it('shows the batai share row only when batai_landowner_share is greater than zero', () => {
    const withBatai = mountBreakdown(makeInvoice({ batai_landowner_share: '1500.00' }))
    expect(withBatai.text()).toContain('Batai Share (Landowner)')
    const withoutBatai = mountBreakdown(makeInvoice({ batai_landowner_share: '0.00' }))
    expect(withoutBatai.text()).not.toContain('Batai Share (Landowner)')
  })
 
  it('shows the grade adjustment banner only when grade_deduction_pct is greater than zero', () => {
    const deducted = mountBreakdown(makeInvoice({ grade_deduction_pct: '12.50' }))
    expect(deducted.text()).toContain('Quality Grade Adjustment Applied')
    const clean = mountBreakdown(makeInvoice({ grade_deduction_pct: '0.00' }))
    expect(clean.text()).not.toContain('Quality Grade Adjustment Applied')
  })
 
  it('grade badge color is driven by grade_deduction_pct, not a fragile string match against grade_received', () => {
    const anyDeduction = mountBreakdown(makeInvoice({ grade_received: 'B+', grade_deduction_pct: '5.00' }))
    expect(anyDeduction.find('.bg-yellow-500').exists()).toBe(true)
    const noDeduction = mountBreakdown(makeInvoice({ grade_received: 'A', grade_deduction_pct: '0.00' }))
    expect(noDeduction.find('.bg-green-400').exists()).toBe(true)
  })
 
  it('shows the insurance-activated banner only when net profit is zero AND insurance_triggered is true', () => {
    const triggered = mountBreakdown(makeInvoice({ farmer_net: '0.00', insurance_triggered: true }))
    expect(triggered.text()).toContain('Insurance Coverage Activated')
    const zeroButNotTriggered = mountBreakdown(makeInvoice({ farmer_net: '0.00', insurance_triggered: false }))
    expect(zeroButNotTriggered.text()).not.toContain('Insurance Coverage Activated')
    const triggeredButNotZero = mountBreakdown(makeInvoice({ farmer_net: '500.00', insurance_triggered: true }))
    expect(triggeredButNotZero.text()).not.toContain('Insurance Coverage Activated')
  })
 
  it('net profit section is styled red when farmer_net is not positive', () => {
    const wrapper = mountBreakdown(makeInvoice({ farmer_net: '0.00' }))
    expect(wrapper.find('.bg-red-50').exists()).toBe(true)
  })
 
  it('formats a missing bank_advanced_at as an em dash instead of "Invalid Date"', () => {
    const wrapper = mountBreakdown(makeInvoice({ bank_advanced_at: null }))
    expect(wrapper.text()).toContain('✓ Credited to your wallet at —')
  })
 
  it('formats gross_payout and expected_payout correctly inside the deduction banner', () => {
    const wrapper = mountBreakdown(makeInvoice({ grade_deduction_pct: '10.00', expected_payout: '50000.00', gross_payout: '45000.00' }))
    expect(wrapper.text()).toContain('Expected: ₨ 50,000')
    expect(wrapper.text()).toContain('Final: ₨ 45,000')
  })
})