import { describe, it, expect, vi, beforeEach } from 'vitest'
import apiClient from '@/api/client.js'
import { 
  getEscrowBalance, 
  getEscrowTransactions, 
  getAFOCaps, 
  payShopkeeper 
} from '@/api/escrow.js'

vi.mock('@/api/client.js', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('Escrow API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('getEscrowBalance hits the confirmed real backend URL', () => {
    getEscrowBalance('escrow-1')
    expect(apiClient.get).toHaveBeenCalledWith('/escrow/wallets/escrow-1/balance/')
  })

  it('getEscrowTransactions hits the confirmed real backend URL and passes params', () => {
    getEscrowTransactions('escrow-1', { page: 2 })
    expect(apiClient.get).toHaveBeenCalledWith('/escrow/wallets/escrow-1/transactions/', { params: { page: 2 } })
  })

  it('getAFOCaps hits the confirmed real backend URL', () => {
    getAFOCaps('escrow-1')
    expect(apiClient.get).toHaveBeenCalledWith('/escrow/wallets/escrow-1/afo_caps/')
  })

  it('payShopkeeper hits the confirmed real backend URL and passes the payload', () => {
    const payload = { amount: '500.00', shopkeeper_id: 'shop-123' }
    payShopkeeper('escrow-1', payload)
    expect(apiClient.post).toHaveBeenCalledWith('/escrow/wallets/escrow-1/pay_shopkeeper/', payload)
  })
})