import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { getMyBalance, listTransactions } from '@/api/wallets.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('wallets api layer', () => {
  it('getMyBalance hits the confirmed real backend URL', () => {
    getMyBalance()
    expect(apiClient.get).toHaveBeenCalledWith('/wallets/balances/my_balance/')
  })

  it('listTransactions hits the confirmed URL and forwards params', () => {
    listTransactions({ txn_type: 'fee' })
    expect(apiClient.get).toHaveBeenCalledWith('/wallets/transactions/', { params: { txn_type: 'fee' } })
  })
})