import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import LoginView from '@/views/auth/LoginView.vue'
import { useAuthStore } from '@/stores/auth.js'

const pushMock = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: pushMock }) }))

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(LoginView, { global: { plugins: [pinia] } })
  return { wrapper, auth: useAuthStore() }
}

describe('auth/LoginView.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('calls auth.login with entered credentials', async () => {
    const { wrapper, auth } = mountComponent()
    auth.login.mockResolvedValue({ role: 'smallholder' })
    await wrapper.find('input[type="text"]').setValue('03001234567')
    await wrapper.find('input[type="password"]').setValue('secret123')
    await wrapper.find('form').trigger('submit')
    expect(auth.login).toHaveBeenCalledWith('03001234567', 'secret123')
  })

  it.each([
    ['smallholder', '/farmer/dashboard'], ['bank', '/bank/dashboard'], ['factory', '/factory/dashboard'],
    ['shopkeeper', '/shopkeeper/dashboard'], ['insurance', '/insurance/dashboard'],
    ['afo', '/afo/dashboard'], ['admin', '/bank/dashboard'],
  ])('redirects role "%s" to %s on success', async (role, expectedPath) => {
    const { wrapper, auth } = mountComponent()
    auth.login.mockResolvedValue({ role })
    await wrapper.find('input[type="text"]').setValue('0300')
    await wrapper.find('input[type="password"]').setValue('pass')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(pushMock).toHaveBeenCalledWith(expectedPath)
  })

  it('does not navigate on a rejected login; relies on store error state', async () => {
    const { wrapper, auth } = mountComponent()
    auth.login.mockRejectedValue({ response: { data: { detail: 'No active account found with the given credentials' } } })
    auth.loginError = 'No active account found with the given credentials'
    await wrapper.find('input[type="text"]').setValue('0300')
    await wrapper.find('input[type="password"]').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(pushMock).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('No active account found with the given credentials')
  })

  it('disables submit and shows progress text while isLoading', async () => {
    const { wrapper, auth } = mountComponent()
    auth.isLoading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('button[type="submit"]').text()).toBe('Logging in...')
  })
})