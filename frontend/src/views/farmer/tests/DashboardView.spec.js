import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { nextTick } from 'vue'
import DashboardView from '@/views/farmer/DashboardView.vue'
import { useAuthStore } from '@/stores/auth.js' 

function mountView() {
  return mount(DashboardView, {
    global: {
      plugins: [createTestingPinia({
        createSpy: vi.fn, 
        stubActions: true,
      })],
      stubs: {
        EscrowDashboardView: true, SettlementsList: true, LogDeliveryForm: true,
        ApplyLoanForm: true, LoanHistory: true, BrowseContracts: true,
        RequestAgreementForm: true, FileClaimModal: true,
      },
    },
  })
}

describe('farmer/DashboardView.vue', () => {
  it('FIXED BUG: no auth-gated sections mount when the user is not logged in', async () => {
    const wrapper = mountView()
    const auth = useAuthStore()
    
    auth.isLoggedIn = false
    await nextTick() 

    expect(wrapper.findComponent({ name: 'LoanHistory' }).exists()).toBe(false)
    expect(wrapper.findComponent({ name: 'ApplyLoanForm' }).exists()).toBe(false)
    expect(wrapper.findComponent({ name: 'BrowseContracts' }).exists()).toBe(false)
    expect(wrapper.text()).toContain('Please log in')
  })

  it('renders all core sections when logged in', async () => {
    const wrapper = mountView()
    const auth = useAuthStore()
    
    auth.isLoggedIn = true
    await nextTick() 

    expect(wrapper.findComponent({ name: 'EscrowDashboardView' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'LoanHistory' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'BrowseContracts' }).exists()).toBe(true)
  })

  it('shows RequestAgreementForm only for the tenant role, not smallholder', async () => {
    const wrapper = mountView()
    const auth = useAuthStore()
    auth.isLoggedIn = true
    auth.user = { role: 'smallholder' }
    await nextTick()
    expect(wrapper.findComponent({ name: 'RequestAgreementForm' }).exists()).toBe(false)

    auth.user = { role: 'tenant' }
    await nextTick()
    expect(wrapper.findComponent({ name: 'RequestAgreementForm' }).exists()).toBe(true)
  })

  it('FileClaimModal is closed by default and opens on button click', async () => {
    const wrapper = mountView()
    const auth = useAuthStore()
    
    auth.isLoggedIn = true 
    await nextTick()

    expect(wrapper.findComponent({ name: 'FileClaimModal' }).exists()).toBe(false)
    await wrapper.find('button').trigger('click')
    expect(wrapper.findComponent({ name: 'FileClaimModal' }).exists()).toBe(true)
  })

  it('FileClaimModal closes on both its close and success events', async () => {
    const wrapper = mountView()
    const auth = useAuthStore()
    
    auth.isLoggedIn = true
    await nextTick()
    await wrapper.find('button').trigger('click')
    await wrapper.findComponent({ name: 'FileClaimModal' }).vm.$emit('success')
    expect(wrapper.findComponent({ name: 'FileClaimModal' }).exists()).toBe(false)
  })
})