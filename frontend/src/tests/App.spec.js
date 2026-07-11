import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createTestingPinia } from '@pinia/testing'
import App from '@/App.vue'

async function mountAt(path) {
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div>page</div>' } }] })
  router.push(path)
  await router.isReady()
  return mount(App, { global: { plugins: [router, createTestingPinia({ createSpy: vi.fn })] } })
}

describe('App.vue', () => {
  it('wraps the router-view in AppShell for a normal authenticated route', async () => {
    const wrapper = await mountAt('/farmer/dashboard')
    expect(wrapper.findComponent({ name: 'AppShell' }).exists() || wrapper.html().includes('flex h-screen')).toBeTruthy()
  })

  it('does NOT wrap AppShell around /login', async () => {
    const wrapper = await mountAt('/login')
    expect(wrapper.html()).not.toContain('flex h-screen')
  })

  it('FIXED BUG: does NOT wrap AppShell around /register either -- it did before', async () => {
    const wrapper = await mountAt('/register')
    expect(wrapper.html()).not.toContain('flex h-screen')
  })

  it('NotificationBanner renders regardless of route', async () => {
    const wrapper = await mountAt('/login')
    expect(wrapper.findComponent({ name: 'NotificationBanner' }).exists()).toBe(true)
  })
})