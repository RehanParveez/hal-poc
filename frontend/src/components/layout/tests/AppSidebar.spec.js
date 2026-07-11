import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createTestingPinia } from '@pinia/testing'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth.js'

async function mountSidebar(role, path = '/farmer/dashboard') {
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }] })
  router.push(path)
  await router.isReady()
  const wrapper = mount(AppSidebar, { global: { plugins: [router, createTestingPinia({ createSpy: vi.fn, stubActions: true })] } })
  const auth = useAuthStore()
  auth.user = { full_name: 'Test User', role, district: 'Faisalabad', province: 'punjab' }
  await wrapper.vm.$nextTick()
  return { wrapper, auth, router }
}

describe('AppSidebar.vue', () => {
  it('renders the correct nav items for a smallholder role', async () => {
    const { wrapper } = await mountSidebar('smallholder')
    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('Escrow')
    expect(wrapper.text()).toContain('Contracts')
  })

  it('renders a different, role-specific menu for bank', async () => {
    const { wrapper } = await mountSidebar('bank')
    expect(wrapper.text()).toContain('Loan Queue')
    expect(wrapper.text()).not.toContain('Log Delivery')
  })

  it('DOCUMENTS A GAP: an unmapped/unknown role silently renders an empty nav, no error', async () => {
    const { wrapper } = await mountSidebar('some_future_role')
    expect(wrapper.findAll('nav a, nav router-link').length).toBe(0)
  })

  it('highlights the router-link matching the current route path', async () => {
    const { wrapper } = await mountSidebar('smallholder', '/farmer/dashboard')
    const activeLink = wrapper.findAll('a').find((a) => a.text().includes('Dashboard'))
    expect(activeLink.classes()).toContain('bg-slate-800')
  })

  it('FIXED: logout now awaits auth.logout() before navigating', async () => {
    const { wrapper, auth, router } = await mountSidebar('smallholder')
    const pushSpy = vi.spyOn(router, 'push')
    let resolveLogout
    auth.logout.mockReturnValue(new Promise((r) => { resolveLogout = r }))
    const clickPromise = wrapper.find('button').trigger('click')
    expect(pushSpy).not.toHaveBeenCalled()
    resolveLogout()
    await clickPromise
    expect(pushSpy).toHaveBeenCalledWith('/login')
  })

  it('shows the authenticated user\'s name and role', async () => {
    const { wrapper } = await mountSidebar('landowner')
    expect(wrapper.text()).toContain('Test User')
    expect(wrapper.text()).toContain('landowner')
  })
})