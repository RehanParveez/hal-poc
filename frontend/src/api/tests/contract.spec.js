import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { createContract, listContracts, allocateToContract, listAllocations } from '@/api/contracts.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('contract api layer', () => {
  it('createContract POSTs to the confirmed real backend URL', () => {
    const payload = { crop: 'c1', required_kg: '5000.00', base_price_per_kg: '40.00', delivery_deadline: '2027-01-01' }
    createContract(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/contracts/cropcontracts/', payload)
  })
  it('listContracts GETs with params', () => {
    listContracts({ status: 'open' })
    expect(apiClient.get).toHaveBeenCalledWith('/contracts/cropcontracts/', { params: { status: 'open' } })
  })
  it('allocateToContract POSTs to the confirmed allocate action with the exact loan_id/committed_kg keys the view reads', () => {
    allocateToContract('c1', { loan_id: 'l1', committed_kg: '200.00' })
    expect(apiClient.post).toHaveBeenCalledWith('/contracts/cropcontracts/c1/allocate/', { loan_id: 'l1', committed_kg: '200.00' })
  })
  it('listAllocations GETs /contracts/allocations/', () => {
    listAllocations()
    expect(apiClient.get).toHaveBeenCalledWith('/contracts/allocations/', { params: undefined })
  })
})