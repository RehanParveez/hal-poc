import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listPolicies, listClaims, fileClaim, reviewClaim } from '@/api/insurance.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))

describe('insurance api layer', () => {
  it('listPolicies GETs /insurance/policies/ with params', () => {
    listPolicies({ status: 'active' })
    expect(apiClient.get).toHaveBeenCalledWith('/insurance/policies/', { params: { status: 'active' } })
  })
  it('listClaims GETs /insurance/claims/ with params', () => {
    listClaims({ status: 'pending' })
    expect(apiClient.get).toHaveBeenCalledWith('/insurance/claims/', { params: { status: 'pending' } })
  })
  it('fileClaim POSTs with policy_id at the top level, matching request.data.get(\'policy_id\')', () => {
    const payload = { policy_id: 'p1', reason: 'Flooding destroyed the standing crop', claim_amount: '15000.00' }
    fileClaim(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/insurance/claims/', payload)
  })
  it('reviewClaim PATCHes the confirmed /review/ action', () => {
    reviewClaim('c1', { decision: 'approved', approved_amount: '9000.00', reviewer_note: 'Verified' })
    expect(apiClient.patch).toHaveBeenCalledWith('/insurance/claims/c1/review/', { decision: 'approved', approved_amount: '9000.00', reviewer_note: 'Verified' })
  })
})