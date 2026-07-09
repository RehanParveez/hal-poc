import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useWalletsStore } from '@/stores/wallets.js'
import * as walletsApi from '@/api/wallets.js'

vi.mock('@/api/wallets.js')

describe('useWalletsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchMyBalance', () => {
    it('stores the wallet data with balance converted to a number', async () => {
      walletsApi.getMyBalance.mockResolvedValue({ data: { id: 'w1', wallet_type: 'farmer', balance: '7000.00' } })
      const store = useWalletsStore()
      await store.fetchMyBalance()
      expect(store.wallet.balance).toBe(7000)
      expect(typeof store.wallet.balance).toBe('number')
    })

    it('sets isLoading true during the request and false after', async () => {
      let resolveFn
      walletsApi.getMyBalance.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useWalletsStore()
      const promise = store.fetchMyBalance()
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { balance: '100.00' } })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('a rejected request sets a readable error and re-throws', async () => {
      walletsApi.getMyBalance.mockRejectedValue({ response: { status: 404, data: { error: 'You do not have a wallet yet.' } } })
      const store = useWalletsStore()
      await expect(store.fetchMyBalance()).rejects.toBeTruthy()
      expect(store.isLoading).toBe(false)
      expect(store.wallet).toBe(null)
      expect(store.error).toBe('You do not have a wallet yet.')
    })
  })

  describe('fetchTransactions', () => {
    it('unwraps the paginated shape and converts amount to a number', async () => {
      walletsApi.listTransactions.mockResolvedValue({
        data: {
          count: 2,
          results: [
            { id: 't1', amount: '50.00' },
            { id: 't2', amount: '10.50' },
          ]
        }
      })
      const store = useWalletsStore()
      await store.fetchTransactions()
      expect(store.transactions).toEqual([{ id: 't1', amount: 50 }, { id: 't2', amount: 10.5 }])
    })

    it('now toggles isLoading the same way fetchMyBalance does', async () => {
      let resolveFn
      walletsApi.listTransactions.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useWalletsStore()
      const promise = store.fetchTransactions()
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { results: [] } })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('a rejected request sets error state and re-throws', async () => {
      walletsApi.listTransactions.mockRejectedValue(new Error('Network Error'))
      const store = useWalletsStore()
      await expect(store.fetchTransactions()).rejects.toThrow('Network Error')
      expect(store.error).toBe('Failed to load transactions.')
    })
  })
})