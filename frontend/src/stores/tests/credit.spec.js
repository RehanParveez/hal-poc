import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCreditStore } from '@/stores/credit.js'
import * as creditApi from '@/api/credit.js'

vi.mock('@/api/credit.js')

describe('credit store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('requestOTP stores the otp_reference returned by the API', async () => {
    creditApi.requestConsentOTP.mockResolvedValue({ data: { otp_reference: 'otp-2328' } })
    const store = useCreditStore()
    await store.requestOTP('loan-1')
    expect(store.otpReference).toBe('otp-2328')
    expect(store.isRequestingOTP).toBe(false)
  })

  it('verifyOTP calls the API with the stored otpReference, not a re-typed one', async () => {
    creditApi.requestConsentOTP.mockResolvedValue({ data: { otp_reference: 'otp-2328' } })
    creditApi.verifyConsentOTP.mockResolvedValue({ data: {} })
    const store = useCreditStore()
    await store.requestOTP('loan-1')
    await store.verifyOTP('654321')
    expect(creditApi.verifyConsentOTP).toHaveBeenCalledWith('otp-2328', '654321')
  })

  it('runCreditCheck sets activeCheck and begins polling', async () => {
    creditApi.triggerCreditCheck.mockResolvedValue({ data: { id: 'check-1', status: 'pending' } })
    creditApi.pollCreditCheckStatus.mockResolvedValue({ data: { id: 'check-1', status: 'pending' } })
    const store = useCreditStore()
    store.otpReference = 'otp-2328'
    await store.runCreditCheck('loan-1')

    expect(store.activeCheck.status).toBe('pending')
    expect(store.pollIntervalId).not.toBeNull()

    await vi.advanceTimersByTimeAsync(3000)
    expect(creditApi.pollCreditCheckStatus).toHaveBeenCalledWith('check-1')
  })

  it('polling stops automatically once a terminal status is reached', async () => {
    creditApi.triggerCreditCheck.mockResolvedValue({ data: { id: 'check-1', status: 'pending' } })
    creditApi.pollCreditCheckStatus.mockResolvedValue({ data: { id: 'check-1', status: 'completed', is_eligible: true } })
    const store = useCreditStore()
    store.otpReference = 'otp-123'
    await store.runCreditCheck('loan-1')

    await vi.advanceTimersByTimeAsync(3000)
    expect(store.pollIntervalId).toBeNull()

    creditApi.pollCreditCheckStatus.mockClear()
    await vi.advanceTimersByTimeAsync(9000)
    expect(creditApi.pollCreditCheckStatus).not.toHaveBeenCalled()
  })

  it('stopPolling is safe to call even if no check ever ran', () => {
    const store = useCreditStore()
    expect(() => store.stopPolling()).not.toThrow()
  })

  it('isApproved requires BOTH status completed AND is_eligible true — not eligible alone', () => {
    const store = useCreditStore()
    store.activeCheck = { status: 'completed', is_eligible: false }
    expect(store.isApproved).toBe(false)
    expect(store.isRejected).toBe(true)

    store.activeCheck = { status: 'pending', is_eligible: true }
    expect(store.isApproved).toBe(false)
  })

  it('startPolling replaces any existing interval rather than stacking a second one', () => {
    const store = useCreditStore()
    store.startPolling('check-1')
    const firstIntervalId = store.pollIntervalId
    store.startPolling('check-1')
    expect(store.pollIntervalId).not.toBe(firstIntervalId)
  })
})