import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { login, refreshToken, register, fetchProfile } from '@/api/auth.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('auth api layer', () => {
  it('login posts to the confirmed real backend URL', () => {
    login('03001234567', 'secret123')
    expect(apiClient.post).toHaveBeenCalledWith('/accounts/tokenobtainpair/', { phone: '03001234567', password: 'secret123' })
  })

  it('refreshToken posts to the confirmed real backend URL', () => {
    refreshToken('refresh-abc')
    expect(apiClient.post).toHaveBeenCalledWith('/accounts/tokenrefresh/', { refresh: 'refresh-abc' })
  })

  it('register hits /accounts/users/ -- URL confirmed, RESPONSE SHAPE unconfirmed pending UserViewSet', () => {
    register({ phone: '03009999999', password: 'x', cnic: '1', full_name: 'Test', role: 'smallholder', district: 'Faisalabad' })
    expect(apiClient.post).toHaveBeenCalledWith('/accounts/users/', expect.any(Object))
  })

  it('fetchProfile hits /accounts/users/profile/ -- ASSUMES a custom @action, unconfirmed', () => {
    fetchProfile()
    expect(apiClient.get).toHaveBeenCalledWith('/accounts/users/profile/')
  })
})