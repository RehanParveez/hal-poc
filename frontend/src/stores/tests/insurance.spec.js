import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useInsuranceStore } from '@/stores/insurance.js'
import * as insuranceApi from '@/api/insurance.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/insurance.js')
vi.mock('@/stores/notifications.js', () => ({ useNotificationsStore: vi.fn() }))

describe('useInsuranceStore', () => {
  let showSuccess, showError
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    showSuccess = vi.fn()
    showError = vi.fn()
    useNotificationsStore.mockReturnValue({ showSuccess, showError })
  })

  describe('fetchPolicies', () => {
    it('converts coverage_amount and premium_amount to numbers', async () => {
      insuranceApi.listPolicies.mockResolvedValue({ data: [{ id: 'p1', coverage_amount: '100000.00', premium_amount: '2500.00' }] })
      const store = useInsuranceStore()
      await store.fetchPolicies()
      expect(store.policies[0]).toMatchObject({ coverage_amount: 100000, premium_amount: 2500 })
    })

    it('correctly resolves the raw-array response -- InsurancePolicyViewSet.list() is confirmed unpaginated, unlike every other endpoint', async () => {
      insuranceApi.listPolicies.mockResolvedValue({ data: [{ id: 'p1' }, { id: 'p2' }] })
      const store = useInsuranceStore()
      await store.fetchPolicies()
      expect(store.policies).toHaveLength(2)
    })

    it('forwards the status param, matching the view\'s manual status_filter handling', async () => {
      insuranceApi.listPolicies.mockResolvedValue({ data: [] })
      const store = useInsuranceStore()
      await store.fetchPolicies({ status: 'expired' })
      expect(insuranceApi.listPolicies).toHaveBeenCalledWith({ status: 'expired' })
    })

    it('sets error state and re-throws on failure', async () => {
      insuranceApi.listPolicies.mockRejectedValue({ response: { data: { error: 'Server error.' } } })
      const store = useInsuranceStore()
      await expect(store.fetchPolicies()).rejects.toBeTruthy()
      expect(store.error).toBe('Server error.')
      expect(store.isLoading).toBe(false)
    })
  })

  describe('fetchClaims', () => {
    it('now toggles isLoading -- absent entirely in the original implementation', async () => {
      let resolveFn
      insuranceApi.listClaims.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useInsuranceStore()
      const promise = store.fetchClaims()
      expect(store.isLoading).toBe(true)
      resolveFn({ data: [] })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('converts claim_amount to a number and preserves a null approved_amount', async () => {
      insuranceApi.listClaims.mockResolvedValue({ data: [{ id: 'c1', claim_amount: '25000.00', approved_amount: null }] })
      const store = useInsuranceStore()
      await store.fetchClaims()
      expect(store.claims[0]).toMatchObject({ claim_amount: 25000, approved_amount: null })
    })

    it('converts approved_amount to a number once a claim has been reviewed', async () => {
      insuranceApi.listClaims.mockResolvedValue({ data: [{ id: 'c1', claim_amount: '25000.00', approved_amount: '20000.00' }] })
      const store = useInsuranceStore()
      await store.fetchClaims()
      expect(store.claims[0].approved_amount).toBe(20000)
    })
  })

  describe('submitClaim', () => {
    it('notifies success and refreshes claims on success', async () => {
      insuranceApi.fileClaim.mockResolvedValue({ data: {} })
      insuranceApi.listClaims.mockResolvedValue({ data: [] })
      const store = useInsuranceStore()
      await store.submitClaim({ policy_id: 'p1', reason: 'Flooding', claim_amount: '15000.00' })
      expect(showSuccess).toHaveBeenCalledWith('insurance claim submitted successfully.')
      expect(insuranceApi.listClaims).toHaveBeenCalled()
    })

    it('FIXED BUG: a failed submission now sets error state and re-throws, instead of silently swallowing the error', async () => {
      insuranceApi.fileClaim.mockRejectedValue({ response: { data: { error: 'You can only file a claim on your own policy.' } } })
      const store = useInsuranceStore()
      await expect(store.submitClaim({ policy_id: 'p1', reason: 'x', claim_amount: '1.00' })).rejects.toBeTruthy()
      expect(store.error).toBe('You can only file a claim on your own policy.')
      expect(showSuccess).not.toHaveBeenCalled()
      expect(showError).toHaveBeenCalledWith('You can only file a claim on your own policy.')
    })

    it('isLoading still resets to false after a failure', async () => {
      insuranceApi.fileClaim.mockRejectedValue(new Error('Network Error'))
      const store = useInsuranceStore()
      await expect(store.submitClaim({})).rejects.toThrow()
      expect(store.isLoading).toBe(false)
    })
  })

  describe('reviewClaim', () => {
    it('includes approved_amount only when decision is approved', async () => {
      insuranceApi.reviewClaim.mockResolvedValue({ data: {} })
      insuranceApi.listClaims.mockResolvedValue({ data: [] })
      const store = useInsuranceStore()
      await store.reviewClaim('c1', 'approved', '9000.00', 'Verified via inspection')
      expect(insuranceApi.reviewClaim).toHaveBeenCalledWith('c1', { decision: 'approved', reviewer_note: 'Verified via inspection', approved_amount: '9000.00' })
    })

    it('omits approved_amount entirely when decision is rejected', async () => {
      insuranceApi.reviewClaim.mockResolvedValue({ data: {} })
      insuranceApi.listClaims.mockResolvedValue({ data: [] })
      const store = useInsuranceStore()
      await store.reviewClaim('c1', 'rejected', null, 'Insufficient evidence')
      const [, payload] = insuranceApi.reviewClaim.mock.calls[0]
      expect(payload).not.toHaveProperty('approved_amount')
    })

    it('now returns res.data and refreshes claims, matching the pattern used by loans/land review-style actions', async () => {
      insuranceApi.reviewClaim.mockResolvedValue({ data: { id: 'c1', status: 'approved' } })
      insuranceApi.listClaims.mockResolvedValue({ data: [] })
      const store = useInsuranceStore()
      const result = await store.reviewClaim('c1', 'approved', '9000.00', '')
      expect(result).toEqual({ id: 'c1', status: 'approved' })
      expect(insuranceApi.listClaims).toHaveBeenCalled()
    })

    it('sets error state and re-throws on failure (e.g. reviewing an already-resolved claim)', async () => {
      insuranceApi.reviewClaim.mockRejectedValue({ response: { data: { error: 'the claim is already approved. cant review again.' } } })
      const store = useInsuranceStore()
      await expect(store.reviewClaim('c1', 'rejected', null, '')).rejects.toBeTruthy()
      expect(store.error).toBe('the claim is already approved. cant review again.')
    })
  })
})