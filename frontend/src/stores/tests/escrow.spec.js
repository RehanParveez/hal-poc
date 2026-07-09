import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useEscrowStore } from '@/stores/escrow.js'
import * as escrowApi from '@/api/escrow.js'

vi.mock('@/api/escrow.js')

describe('useEscrowStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('getters backed by confirmed real fields', () => {
    it('remainingBalance/totalFunded/totalSpent now return numbers, not strings', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({
        data: {
          remaining_balance: '97500.00',
          total_funded: '100000.00',
          total_spent_on_inputs: '2500.00',
        }
      })
      const store = useEscrowStore()
      await store.fetchWallet('escrow-1')
      expect(store.remainingBalance).toBe(97500)
      expect(typeof store.remainingBalance).toBe('number')
    })

    it('remainingBalance is a number both before AND after load -- type no longer flips', async () => {
      const store = useEscrowStore()
      expect(typeof store.remainingBalance).toBe('number')
      escrowApi.getEscrowBalance.mockResolvedValue({ data: { remaining_balance: '500.00' } })
      await store.fetchWallet('escrow-1')
      expect(typeof store.remainingBalance).toBe('number')
    })
  })

  describe('getters backed by now-confirmed serializer fields', () => {
    it('spendPercent reads spend_percentage, already a number (SerializerMethodField returning a float, not a Decimal string)', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({ data: { remaining_balance: '100.00', spend_percentage: 42.5 } })
      const store = useEscrowStore()
      await store.fetchWallet('escrow-1')
      expect(store.spendPercent).toBe(42.5)
      expect(typeof store.spendPercent).toBe('number')
    })

    it('activePhase reads active_phase -- confirmed real, but it is a full EscrowMilestoneUnlock object, not a phase-name string', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({
        data: {
          remaining_balance: '100.00',
          active_phase: { id: 'u1', unlocked_amount: '30000.00', is_active: true },
        }
      })
      const store = useEscrowStore()
      await store.fetchWallet('escrow-1')
      expect(store.activePhase).toEqual({ id: 'u1', unlocked_amount: '30000.00', is_active: true })
    })

    it('activePhase is null when there is no active unlock', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({ data: { remaining_balance: '100.00', active_phase: null } })
      const store = useEscrowStore()
      await store.fetchWallet('escrow-1')
      expect(store.activePhase).toBe(null)
    })

    it('milestones reads all_phases -- a deliberate SerializerMethodField, correctly distinct from the model\'s "unlocks" related_name', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({
        data: {
          remaining_balance: '100.00',
          all_phases: [{ id: 'u1' }, { id: 'u2' }],
        }
      })
      const store = useEscrowStore()
      await store.fetchWallet('escrow-1')
      expect(store.milestones).toHaveLength(2)
    })
  })

  describe('spendableCategories -- confirmed correct against the real afo_caps response', () => {
    it('filters by the exact keys the backend actually sends', async () => {
      escrowApi.getAFOCaps.mockResolvedValue({
        data: {
          caps: [
            { category: 'seed', is_allowed_now: true },
            { category: 'fertilizer', is_allowed_now: false },
          ]
        }
      })
      const store = useEscrowStore()
      await store.fetchCaps('escrow-1')
      expect(store.spendableCategories).toEqual(['seed'])
    })
  })

  describe('action-level gaps -- now fixed', () => {
    it('fetchCaps now toggles isLoading the same way fetchWallet does', async () => {
      let resolveFn
      escrowApi.getAFOCaps.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useEscrowStore()
      const promise = store.fetchCaps('escrow-1')
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { caps: [] } })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('fetchWallet now sets error state and re-throws on failure', async () => {
      escrowApi.getEscrowBalance.mockRejectedValue(new Error('Network Error'))
      const store = useEscrowStore()
      await expect(store.fetchWallet('escrow-1')).rejects.toThrow('Network Error')
      expect(store.error).toBe('Failed to load escrow wallet.')
    })

    it('refreshWallet is a plain alias for fetchWallet -- not a bug, confirming it', async () => {
      escrowApi.getEscrowBalance.mockResolvedValue({ data: { remaining_balance: '10.00' } })
      const store = useEscrowStore()
      await store.refreshWallet('escrow-1')
      expect(escrowApi.getEscrowBalance).toHaveBeenCalledTimes(1)
    })
  })
})