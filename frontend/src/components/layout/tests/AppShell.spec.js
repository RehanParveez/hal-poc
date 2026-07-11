import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createTestingPinia } from '@pinia/testing'
import AppShell from '@/components/layout/AppShell.vue'

describe('AppShell.vue', () => {
  it('renders slot content inside the layout', async () => {
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }] })
    router.push('/')
    await router.isReady()
    const wrapper = mount(AppShell, {
      slots: { default: '<div class="page-content">Hello</div>' },
      global: { plugins: [router, createTestingPinia({ createSpy: vi.fn })] },
    })
    expect(wrapper.find('.page-content').exists()).toBe(true)
  })
})