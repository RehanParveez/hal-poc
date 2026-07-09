import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSettlementsStore } from '@/stores/settlements.js'
import * as settlementsApi from '@/api/settlements.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/settlements.js')
vi.mock('@/stores/notifications.js')

describe('useSettlementsStore', () => {
  let notifyMock
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    notifyMock = { showSuccess: vi.fn(), showError: vi.fn() }
    useNotificationsStore.mockReturnValue(notifyMock)
  })

  describe('fetchInvoices', () => {
    it('unwraps the paginated results shape correctly', async () => {
      settlementsApi.listInvoices.mockResolvedValue({ data: { count: 1, results: [{ id: 'i1', status: 'pending' }] } })
      const store = useSettlementsStore()
      await store.fetchInvoices()
      expect(store.invoices).toEqual([{ id: 'i1', status: 'pending' }])
    })
  })

  describe('fetchInvoice', () => {
    it('now toggles isLoading, matching fetchInvoices (previously it did not)', async () => {
      let resolveFn
      settlementsApi.getInvoice.mockReturnValue(new Promise((r) => { resolveFn = r }))
      const store = useSettlementsStore()
      const promise = store.fetchInvoice('i1')
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { id: 'i1' } })
      await promise
      expect(store.isLoading).toBe(false)
    })
  })

  describe('factorySettle', () => {
    it('shows success using the real backend message field', async () => {
      settlementsApi.factorySettle.mockResolvedValue({ data: { message: 'Factory settlement confirmed. Bank wallet credited.', invoice: { id: 'i1', status: 'factsettl' } } })
      settlementsApi.listInvoices.mockResolvedValue({ data: { results: [] } })
      const store = useSettlementsStore()
      await store.factorySettle('i1')
      expect(notifyMock.showSuccess).toHaveBeenCalledWith('Factory settlement confirmed. Bank wallet credited.')
    })

    it('FIXED: updates currentInvoice in place when it is the invoice being viewed', async () => {
      settlementsApi.getInvoice.mockResolvedValue({ data: { id: 'i1', status: 'advanced' } })
      settlementsApi.factorySettle.mockResolvedValue({ data: { message: 'ok', invoice: { id: 'i1', status: 'factsettl' } } })
      settlementsApi.listInvoices.mockResolvedValue({ data: { results: [] } })
      const store = useSettlementsStore()
      await store.fetchInvoice('i1')
      expect(store.currentInvoice.status).toBe('advanced')
      await store.factorySettle('i1')
      expect(store.currentInvoice.status).toBe('factsettl')
    })

    it('FIXED: a rejected settlement now surfaces via showError instead of vanishing', async () => {
      settlementsApi.factorySettle.mockRejectedValue({ response: { data: { error: "this invoice has already been process. or cant be settled." } } })
      const store = useSettlementsStore()
      await expect(store.factorySettle('i1')).rejects.toBeTruthy()
      expect(notifyMock.showError).toHaveBeenCalled()
      expect(notifyMock.showSuccess).not.toHaveBeenCalled()
    })

    it('uses a dedicated isSettling flag, separate from the list-loading flag', async () => {
      let resolveFn
      settlementsApi.factorySettle.mockReturnValue(new Promise((r) => { resolveFn = r }))
      const store = useSettlementsStore()
      const promise = store.factorySettle('i1')
      expect(store.isSettling).toBe(true)
      expect(store.isLoading).toBe(false)
      resolveFn({ data: { message: 'ok', invoice: { id: 'i1' } } })
      await promise
      expect(store.isSettling).toBe(false)
    })
  })

  describe('decimal fields -- ten money fields on this model, all strings', () => {
    it('gross_payout and farmer_net_profit are stored as raw strings, unconverted', async () => {
      settlementsApi.getInvoice.mockResolvedValue({ data: { id: 'i1', gross_payout: '100000.00', farmer_net_profit: '92000.00' } })
      const store = useSettlementsStore()
      await store.fetchInvoice('i1')
      expect(typeof store.currentInvoice.gross_payout).toBe('string')
      expect(typeof store.currentInvoice.farmer_net_profit).toBe('string')
    })
  })
})