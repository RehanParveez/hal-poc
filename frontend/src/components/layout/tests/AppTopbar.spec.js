import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createTestingPinia } from '@pinia/testing'
import AppTopbar from '@/components/layout/AppTopbar.vue'
import { useAuthStore } from '@/stores/auth.js'

const KNOWN_DASHBOARD_PATHS = {
  '/farmer/dashboard': 'Farmer Dashboard', '/landowner/dashboard': 'Landowner Dashboard',
  '/bank/dashboard': 'Loan Approval Queue', '/factory/dashboard': 'Factory Dashboard',
  '/shopkeeper/dashboard': 'Shopkeeper Dashboard', '/insurance/dashboard': 'Insurance Dashboard',
  '/afo/dashboard': 'AFO Dashboard',
}

async function mountAt(path, role = 'smallholder') {
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }] })
  router.push(path)
  await router.isReady()
  const wrapper = mount(AppTopbar, { global: { plugins: [router, createTestingPinia({ createSpy: vi.fn })] } })
  const auth = useAuthStore()
  auth.user = { role, district: 'Faisalabad', province: 'punjab' }
  await wrapper.vm.$nextTick()
  return wrapper
}

describe('AppTopbar.vue', () => {
  it.each(Object.entries(KNOWN_DASHBOARD_PATHS))('shows the correct title for %s', async (path, title) => {
    const wrapper = await mountAt(path)
    expect(wrapper.text()).toContain(title)
  })

  it('falls back to "FasalPay" for an unmapped path', async () => {
    const wrapper = await mountAt('/some/unmapped/path')
    expect(wrapper.text()).toContain('FasalPay')
  })

  it('shows the user\'s district and province', async () => {
    const wrapper = await mountAt('/farmer/dashboard')
    expect(wrapper.text()).toContain('Faisalabad')
    expect(wrapper.text()).toContain('punjab')
  })
})