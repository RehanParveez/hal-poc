import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listLands, createLand, createAgreement, listAgreements, approveAgreement, rejectAgreement } from '@/api/land.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))

describe('land api layer', () => {
  it('listLands GETs /land/lands/ with params', () => {
    listLands({ district: 'Faisalabad' })
    expect(apiClient.get).toHaveBeenCalledWith('/land/lands/', { params: { district: 'Faisalabad' } })
  })
  it('createLand POSTs the payload untouched', () => {
    const payload = { parcel_ref: 'PR-1', district: 'Faisalabad', total_acres: '10.00' }
    createLand(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/land/lands/', payload)
  })
  it('createAgreement POSTs the payload untouched', () => {
    const payload = { tenant_phone: '03001234567', parcel: 'p1', agreement_type: 'theka' }
    createAgreement(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/land/agreements/', payload)
  })
  it('listAgreements GETs with params', () => {
    listAgreements({ district: 'Lahore' })
    expect(apiClient.get).toHaveBeenCalledWith('/land/agreements/', { params: { district: 'Lahore' } })
  })
  it('approveAgreement PATCHes with no body', () => {
    approveAgreement('a1')
    expect(apiClient.patch).toHaveBeenCalledWith('/land/agreements/a1/approve/')
  })
  it('rejectAgreement PATCHes with the exact "reason" key the backend reads via request.data.get(\'reason\')', () => {
    rejectAgreement('a1', 'Land needed for own use')
    expect(apiClient.patch).toHaveBeenCalledWith('/land/agreements/a1/reject/', { reason: 'Land needed for own use' })
  })
})