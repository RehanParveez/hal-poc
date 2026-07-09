import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listLoans, getLoan, applyForLoan, approveLoan, rejectLoan, disburseLoan } from '@/api/loans.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))

describe('loans api layer', () => {
  it('listLoans GETs /loans/applications/ with params', () => {
    listLoans({ status: 'submitted' })
    expect(apiClient.get).toHaveBeenCalledWith('/loans/applications/', { params: { status: 'submitted' } })
  })

  it('getLoan GETs a single loan by id', () => {
    getLoan('l1')
    expect(apiClient.get).toHaveBeenCalledWith('/loans/applications/l1/')
  })

  it('applyForLoan POSTs the payload untouched', () => {
    const payload = { crop: 'wheat-id', acres_applied_for: '5.00', requested_amount: '50000.00' }
    applyForLoan(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/loans/applications/', payload)
  })

  it('approveLoan PATCHes the approve action with the payload', () => {
    const payload = { approved_amount: '95000.00', interest_rate_pct: '12.00' }
    approveLoan('l1', payload)
    expect(apiClient.patch).toHaveBeenCalledWith('/loans/applications/l1/approve/', payload)
  })

  it('rejectLoan PATCHes the reject action with the payload', () => {
    rejectLoan('l1', { rejection_reason: 'Low credit score' })
    expect(apiClient.patch).toHaveBeenCalledWith('/loans/applications/l1/reject/', { rejection_reason: 'Low credit score' })
  })

  it('disburseLoan POSTs to the disburse action with no body', () => {
    disburseLoan('l1')
    expect(apiClient.post).toHaveBeenCalledWith('/loans/applications/l1/disburse/')
  })
})