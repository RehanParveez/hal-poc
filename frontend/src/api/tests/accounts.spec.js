import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listBanks, listShopkeepers } from '@/api/accounts.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('accounts api layer -- URLs confirmed against real urls.py + views.py', () => {
  it('listBanks hits the confirmed real backend URL', () => {
    listBanks()
    expect(apiClient.get).toHaveBeenCalledWith('/accounts/users/banks/')
  })

  it('listShopkeepers hits the confirmed real backend URL', () => {
    listShopkeepers()
    expect(apiClient.get).toHaveBeenCalledWith('/accounts/users/shopkeepers/')
  })

  it('DOCUMENTS A PRIVACY GAP: this function adds no role-scoping on top of an unrestricted backend action', () => {
    listShopkeepers()
    expect(apiClient.get).toHaveBeenCalledWith('/accounts/users/shopkeepers/')
  })
})