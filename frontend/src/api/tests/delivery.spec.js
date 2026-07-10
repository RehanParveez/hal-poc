import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listBatches, createBatch, markReceived, confirmGrade } from '@/api/delivery.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))

describe('delivery api layer', () => {
  it('listBatches GETs /delivery/batches/ with params', () => {
    listBatches({ status: 'in_transit' })
    expect(apiClient.get).toHaveBeenCalledWith('/delivery/batches/', { params: { status: 'in_transit' } })
  })
  it('createBatch POSTs the payload untouched', () => {
    const payload = { allocation: 'alloc-1', batch_kg: '10.00' }
    createBatch(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/delivery/batches/', payload)
  })
  it('markReceived PATCHes with no body -- UNCONFIRMED action name, apps/delivery/views.py never shared', () => {
    markReceived('b1')
    expect(apiClient.patch).toHaveBeenCalledWith('/delivery/batches/b1/mark_received/')
  })
  it('confirmGrade PATCHes the payload untouched', () => {
    confirmGrade('b1', { grade_received: 'A', grade_deduction_pct: 5, grade_notes: '' })
    expect(apiClient.patch).toHaveBeenCalledWith('/delivery/batches/b1/confirm_grade/', { grade_received: 'A', grade_deduction_pct: 5, grade_notes: '' })
  })
})