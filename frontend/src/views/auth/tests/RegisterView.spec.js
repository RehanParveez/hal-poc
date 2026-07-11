import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import RegisterView from '@/views/auth/RegisterView.vue'
import { useAuthStore } from '@/stores/auth.js'

const pushMock = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: pushMock }) }))

function mountComponent() {
  const pinia = createTestingPinia({ createSpy: vi.fn, stubActions: true })
  const wrapper = mount(RegisterView, { global: { plugins: [pinia] } })
  return { wrapper, auth: useAuthStore() }
}
async function fillValid(wrapper, role = 'smallholder') {
  await wrapper.find('input[placeholder="e.g., Muhammad Ali"]').setValue('Test Farmer')
  await wrapper.find('input[placeholder="03001234567"]').setValue('03001234567')
  await wrapper.find('input[placeholder="35202-1234567-1"]').setValue('35202-1234567-1')
  await wrapper.find('input[type="password"]').setValue('secret123')
  await wrapper.find('select').setValue(role)
  await wrapper.find('input[placeholder="e.g., Faisalabad"]').setValue('Faisalabad')
}

describe('auth/RegisterView.vue', () => {
  beforeEach(() => vi.clearAllMocks())

  it('THE headline security fix: institutional roles are no longer offered on the public signup form', () => {
    const { wrapper } = mountComponent()
    const values = wrapper.findAll('option').map((o) => o.attributes('value'))
    expect(values).not.toContain('admin')
    expect(values).not.toContain('bank')
    expect(values).not.toContain('factory')
    expect(values).not.toContain('insurance')
    expect(values).not.toContain('afo')
  })

  it('only the four public individual roles remain selectable', () => {
    const { wrapper } = mountComponent()
    const values = wrapper.findAll('option').map((o) => o.attributes('value')).filter(Boolean)
    expect(values).toEqual(['smallholder', 'tenant', 'landowner', 'shopkeeper'])
  })

  it('submits the full payload to auth.register', async () => {
    const { wrapper, auth } = mountComponent()
    auth.register.mockResolvedValue({ role: 'smallholder' })
    await fillValid(wrapper)
    await wrapper.find('form').trigger('submit')
    expect(auth.register).toHaveBeenCalledWith({
      full_name: 'Test Farmer', phone: '03001234567', cnic: '35202-1234567-1',
      password: 'secret123', role: 'smallholder', district: 'Faisalabad', province: 'Punjab',
    })
  })

  it('redirects to the correct dashboard on success', async () => {
    const { wrapper, auth } = mountComponent()
    auth.register.mockResolvedValue({ role: 'landowner' })
    await fillValid(wrapper, 'landowner')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(pushMock).toHaveBeenCalledWith('/landowner/dashboard')
  })

  it('surfaces a duplicate phone/cnic backend error and does not navigate', async () => {
    const { wrapper, auth } = mountComponent()
    auth.register.mockRejectedValue({ response: { data: { phone: ['user with this phone already exists.'] } } })
    await fillValid(wrapper)
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('user with this phone already exists.')
    expect(pushMock).not.toHaveBeenCalled()
  })

  it('disables submit and shows progress text while submitting', async () => {
    let resolveFn
    const { wrapper, auth } = mountComponent()
    auth.register.mockReturnValue(new Promise((r) => { resolveFn = r }))
    await fillValid(wrapper)
    const submitPromise = wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.find('button[type="submit"]').text()).toBe('Creating account...')
    resolveFn({ role: 'smallholder' })
    await submitPromise
  })

  it('province defaults to Punjab and is sent unedited', async () => {
    const { wrapper, auth } = mountComponent()
    auth.register.mockResolvedValue({ role: 'smallholder' })
    await fillValid(wrapper)
    await wrapper.find('form').trigger('submit')
    expect(auth.register).toHaveBeenCalledWith(expect.objectContaining({ province: 'Punjab' }))
  })
})