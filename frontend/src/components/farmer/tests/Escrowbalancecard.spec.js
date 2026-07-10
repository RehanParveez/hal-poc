import { beforeEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EscrowBalanceCard from '@/components/farmer/EscrowBalanceCard.vue'
import { useEscrowStore } from '@/stores/escrow.js'
 
function mountCard() {
  return mount(EscrowBalanceCard, { global: { stubs: { InsuranceBadge: true } } })
}
 
describe('EscrowBalanceCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
 
  it('renders remaining and total funded balances formatted as rounded PKR', () => {
    const store = useEscrowStore()
    store.wallet = { remaining_balance: '4500.75', total_funded: '10000.00', total_spent_on_inputs: '0' }
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('₨ 4,501')
    expect(wrapper.text()).toContain('₨ 10,000')
  })
 
  it('binds the spend progress bar width to spendPercent', () => {
    const store = useEscrowStore()
    store.wallet = { remaining_balance: '0', total_funded: '1000', spend_percentage: 42 }
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('42%')
    const bar = wrapper.find('.bg-green-600')
    expect(bar.attributes('style')).toContain('width: 42%')
  })
 
  it('shows the active phase block with phase number, name, and allowed input categories', () => {
    const store = useEscrowStore()
    store.wallet = {
      remaining_balance: '0', total_funded: '0',
      active_phase: { phase_number: 1, phase_name: 'Sowing', allowed_input_categories: ['seed', 'fertilizer'] },
    }
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Phase 1: Sowing')
    expect(wrapper.text()).toContain('Allowed: seed, fertilizer')
  })
 
  it('hides the active phase block entirely when there is no active phase', () => {
    const store = useEscrowStore()
    store.wallet = { remaining_balance: '0', total_funded: '0', active_phase: null }
    const wrapper = mountCard()
    expect(wrapper.text()).not.toContain('Allowed:')
  })
 
  it('does not crash when the active phase has no allowed_input_categories at all', () => {
    const store = useEscrowStore()
    store.wallet = { remaining_balance: '0', total_funded: '0', active_phase: { phase_number: 1, phase_name: 'Sowing' } }
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Phase 1: Sowing')
  })
 
  it('shows a loading state and hides the balance while isLoading is true', () => {
    const store = useEscrowStore()
    store.isLoading = true
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Loading escrow balance')
    expect(wrapper.text()).not.toContain('Escrow Balance')
  })
 
  it('shows the store error message instead of a stale or zeroed-out balance', () => {
    const store = useEscrowStore()
    store.error = 'Escrow not found.'
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Escrow not found.')
    expect(wrapper.text()).not.toContain('Escrow Balance')
  })
 
  it('formats a null or undefined balance as ₨ 0 instead of ₨ NaN', () => {
    const store = useEscrowStore()
    store.wallet = { remaining_balance: null, total_funded: undefined }
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('₨ 0')
  })
})