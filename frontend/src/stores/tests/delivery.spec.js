import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDeliveryStore } from '@/stores/delivery.js'
import * as deliveryApi from '@/api/delivery.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/delivery.js')
vi.mock('@/stores/notifications.js')

describe('useDeliveryStore', () => {
  let notifyMock
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    notifyMock = { showSuccess: vi.fn(), showError: vi.fn() }
    useNotificationsStore.mockReturnValue(notifyMock)
  })

  describe('fetchBatches', () => {
    it('unwraps the paginated results shape', async () => {
      deliveryApi.listBatches.mockResolvedValue({ data: { count: 1, results: [{ id: 'b1', status: 'in_transit' }] } })
      const store = useDeliveryStore()
      await store.fetchBatches()
      expect(store.batches).toEqual([{ id: 'b1', status: 'in_transit' }])
    })
  })

  describe('markReceived', () => {
    it('FIXED: a rejected request now surfaces via showError instead of vanishing', async () => {
      deliveryApi.markReceived.mockRejectedValue({ response: { data: { error: "this batch doesn't belong to your contract." } } })
      const store = useDeliveryStore()
      await expect(store.markReceived('b1')).rejects.toBeTruthy()
      expect(notifyMock.showError).toHaveBeenCalledWith("this batch doesn't belong to your contract.")
    })

    it('FIXED: isMutating now toggles around this action', async () => {
      let resolveFn
      deliveryApi.markReceived.mockReturnValue(new Promise((r) => { resolveFn = r }))
      const store = useDeliveryStore()
      const promise = store.markReceived('b1')
      expect(store.isMutating).toBe(true)
      deliveryApi.listBatches.mockResolvedValue({ data: { results: [] } })
      resolveFn({ data: { message: 'ok' } })
      await promise
      expect(store.isMutating).toBe(false)
    })
  })

  describe('createBatch', () => {
    it('sends the two fields the real view expects', async () => {
      deliveryApi.createBatch.mockResolvedValue({ data: {} })
      deliveryApi.listBatches.mockResolvedValue({ data: { results: [] } })
      const store = useDeliveryStore()
      await store.createBatch('alloc-1', '10.00')
      expect(deliveryApi.createBatch).toHaveBeenCalledWith({ allocation: 'alloc-1', batch_kg: '10.00' })
    })

    it('FIXED: a rejected request (e.g. exceeding committed_kg) now surfaces via showError', async () => {
      deliveryApi.createBatch.mockRejectedValue({ response: { data: { error: 'cant deliver 50kg. You committed 100kg and have already delivered 60kg.' } } })
      const store = useDeliveryStore()
      await expect(store.createBatch('alloc-1', '50.00')).rejects.toBeTruthy()
      expect(notifyMock.showError).toHaveBeenCalled()
    })

    it('KNOWN GAP: sends a negative batch_kg with zero client-side resistance', async () => {
      deliveryApi.createBatch.mockResolvedValue({ data: {} })
      deliveryApi.listBatches.mockResolvedValue({ data: { results: [] } })
      const store = useDeliveryStore()
      await store.createBatch('alloc-1', '-25.00')
      expect(deliveryApi.createBatch).toHaveBeenCalledWith({ allocation: 'alloc-1', batch_kg: '-25.00' })
    })
  })

  describe('confirmGrade', () => {
    it('THE headline fix: a rejected confirm now actually rejects the returned promise', async () => {
      deliveryApi.confirmGrade.mockRejectedValue({ response: { data: { error: "cant confirm the grade on a batch with status 'grade_confirmed'." } } })
      const store = useDeliveryStore()
      await expect(store.confirmGrade('b1', 'A', 5, '')).rejects.toBeTruthy()
      expect(notifyMock.showError).toHaveBeenCalledWith(expect.stringContaining('cant confirm the grade'))
      expect(notifyMock.showSuccess).not.toHaveBeenCalled()
    })

    it('does not refresh the batch list when the request fails', async () => {
      deliveryApi.confirmGrade.mockRejectedValue({ response: { data: {} } })
      const store = useDeliveryStore()
      await expect(store.confirmGrade('b1', 'A', 5, '')).rejects.toBeTruthy()
      expect(deliveryApi.listBatches).not.toHaveBeenCalled()
    })

    it('sends exactly the three fields GradeConfirmationSerializer expects', async () => {
      deliveryApi.confirmGrade.mockResolvedValue({ data: { message: 'ok' } })
      deliveryApi.listBatches.mockResolvedValue({ data: { results: [] } })
      const store = useDeliveryStore()
      await store.confirmGrade('b1', 'A', 5, 'minor damage')
      expect(deliveryApi.confirmGrade).toHaveBeenCalledWith('b1', {
        grade_received: 'A', grade_deduction_pct: 5, grade_notes: 'minor damage',
      })
    })
  })
})