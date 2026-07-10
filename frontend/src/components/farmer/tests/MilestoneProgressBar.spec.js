import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import MilestoneProgressBar from '@/components/farmer/MilestoneProgressBar.vue'
import { useEscrowStore } from '@/stores/escrow.js'

describe('MilestoneProgressBar.vue', () => {
  it('FIXED BUG: re-renders once store data arrives after mount, instead of freezing on the pre-load empty state', async () => {
    const wrapper = mount(MilestoneProgressBar, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } })
    expect(wrapper.text()).not.toContain('Phase 1')
    const escrow = useEscrowStore()
    escrow.wallet = { all_phases: [{ id: 'u1', phase_number: 1, phase_name: 'Sowing', is_active: true, unlocked_at: '2026-01-01', day_offset: 0, allowed_categories: ['seed'] }] }
    await flushPromises()
    expect(wrapper.text()).toContain('Phase 1: Sowing')
  })

  it('renders the completed state -- unlocked_at set, is_active false', async () => {
    const wrapper = mount(MilestoneProgressBar, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } })
    const escrow = useEscrowStore()
    escrow.wallet = { all_phases: [{ id: 'u1', phase_number: 1, phase_name: 'Sowing', is_active: false, unlocked_at: '2026-01-01' }] }
    await flushPromises()
    expect(wrapper.find('.bg-green-600.border-green-600').exists()).toBe(true)
    expect(wrapper.text()).toContain('✓')
  })

  it('renders the active state with the ACTIVE badge and allowed-category chips', async () => {
    const wrapper = mount(MilestoneProgressBar, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } })
    const escrow = useEscrowStore()
    escrow.wallet = { all_phases: [{ id: 'u1', phase_number: 2, phase_name: 'Growth', is_active: true, unlocked_at: '2026-02-01', allowed_categories: ['fertilizer', 'pesticide'] }] }
    await flushPromises()
    expect(wrapper.text()).toContain('ACTIVE')
    expect(wrapper.text()).toContain('fertilizer')
  })

  it('renders the locked state for the given function behavior -- UNCONFIRMED whether real API data ever produces this, since all_phases only returns already-reached phases', async () => {
    const wrapper = mount(MilestoneProgressBar, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } })
    const escrow = useEscrowStore()
    escrow.wallet = { all_phases: [{ id: 'u1', phase_number: 3, phase_name: 'Harvest', is_active: false, unlocked_at: null, day_offset: 90 }] }
    await flushPromises()
    expect(wrapper.text()).toContain('🔒')
    expect(wrapper.text()).toContain('unlocks Day 90')
  })

  it('does not render a connector line after the last milestone', async () => {
    const wrapper = mount(MilestoneProgressBar, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } })
    const escrow = useEscrowStore()
    escrow.wallet = { all_phases: [{ id: 'u1', phase_number: 1, phase_name: 'Sowing', is_active: true, unlocked_at: '2026-01-01' }] }
    await flushPromises()
    expect(wrapper.find('.w-0\\.5.flex-1').exists()).toBe(false)
  })
})